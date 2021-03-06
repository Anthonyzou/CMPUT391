import ast, cassandra
from cassandra.cluster import Cluster
import random, sys
import string, timeit
import uuid, Queue


def randword(length): return ''.join(random.choice(string.lowercase) for i in range(length))

Consist_Level = 0
acluster = 0
datadate = 1385305327 #equal to 2013-11-24 08:02:07-0700
session = None
SEIZ_CELL_NUM_L = None
def generate(label, element_type, frequency):
    global acluster, session, datadate, SEIZ_CELL_NUM_L

    # column-specific data
    if (label == "MOBILE_ID_TYPE"):  # pretend this is partition by cluster
        result = acluster % 8
        session.execute_async(
                session.prepare("insert into group_by_MOBILE_ID_TYPE (MOBILE_ID_TYPE, id) values (?,?)")
                .bind([result, SEIZ_CELL_NUM_L]))
        acluster += 1
    elif label == "SEIZ_CELL_NUM_L":
        result = uuid.uuid4()
        SEIZ_CELL_NUM_L = result
    elif (label == "MONTH_DAY"):
        result = random.randint(1, 31)
        session.execute_async(
                session.prepare("insert into group_by_month (MONTH_DAY, id) values (?,?)")
                .bind([result, SEIZ_CELL_NUM_L]))
    elif (label == "LONGITUDE" or label == "LAST_LONGITUDE"):
        result = random.random() * 360 - 180
    elif (label == "LATITUDE" or label == "LAST_LATITUDE"):
        result = random.random() * 180 - 90
    # type-specific fallback data
    elif (element_type == "float"):
        result = random.random()
    elif (element_type == "text"):
        result = randword(16)
    elif (element_type == "timestamp"):
        result = datadate
    else:
        result = random.randint(0, 9900000)
    return result


if __name__ == '__main__':
    start_time = timeit.default_timer()
    cluster = Cluster(['10.1.0.104 ', '10.1.0.105', '127.0.0.1'], port=9233)
    session = cluster.connect() 
    cluster.control_connection_timeout =  cluster.default_timeout = None
    
    print cluster.metadata.cluster_name # cluster should be our own
    print cluster.cql_version, cassandra.__version__ ,"\n"
    
    seed = 3333
        # read table stuffs from sample table schema
    with open("tableFrequency.txt") as tables_freq:
        (labels, counts) = tables_freq
    labels = ast.literal_eval(labels)  # turn input into list correctly
    counts = ast.literal_eval(counts)  # turn input into list correctly
    smallLabels = labels[:len(labels)/2]
    try:
        seed = int(sys.argv[2])
        session.set_keyspace("group3alt")
    except: 
        session.execute("drop keyspace if exists group3alt")
        session.execute("""CREATE KEYSPACE group3alt 
                           WITH REPLICATION = { 'class' : 'SimpleStrategy','replication_factor' : 3 } 
                           AND durable_writes = false""")
        session.set_keyspace("group3alt")
        cols = "".join(i[0]+" "+i[1]+"," for i in labels)
        smallcols = "".join(i[0]+" "+i[1]+"," for i in labels[:len(labels)/2])
        for setupcmd in ["CREATE TABLE cdr(" + cols + """primary key(SEIZ_CELL_NUM_L,MSC_CODE ,CITY_ID,SERVICE_NODE_ID
                         ,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
                         SESS_SFC, CFC,SM_CONUT1, SM_CONUT2 ,SM_CONUT3 ,SM_CONUT4 ,SM_CONUT5 ,SM_CONUT6 )) 
                         with compression={ 'sstable_compression':''} and clustering order by (msc_code asc)"""
                        ,"CREATE TABLE smallcdr(" + smallcols + """primary key(SEIZ_CELL_NUM_L,MSC_CODE ,CITY_ID,SERVICE_NODE_ID
                        ,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
                         SESS_SFC, CFC)) 
                         with compression={ 'sstable_compression':''} and clustering order by (msc_code asc)"""
                        ,"CREATE TABLE cdr_alt(" + cols + """primary key(SEIZ_CELL_NUM_L,MSC_CODE ,CITY_ID,SERVICE_NODE_ID
                        ,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
                         SESS_SFC, CFC)) 
                         with compression={ 'sstable_compression':''} and clustering order by (msc_code asc)"""
                        ,"Create table group_by_month (MONTH_DAY int, id uuid, primary key (month_day, id))"
                        ,"Create table group_by_MOBILE_ID_TYPE (MOBILE_ID_TYPE int, id uuid, primary key (MOBILE_ID_TYPE,id))"
                        ]:
            try: session.execute(setupcmd)
            except Exception as error: print error
    random.seed(seed)
    
    body = "".join(i[0]+"," for i in labels)[:-1] + ") VALUES (" + ("?," * (len(labels) - 1)) + "?)"
    smallbody = "".join(i[0]+"," for i in smallLabels)[:-1] + ") VALUES (" + ("?," * (len(smallLabels) - 1)) + "?)"
    # remove last char
    # build question marks for binding
    prepared = session.prepare("INSERT INTO cdr ("+ body )
    prepared1 = session.prepare("INSERT INTO cdr_alt ("+ body )
    prepared2 = session.prepare("INSERT INTO smallcdr ("+ smallbody )
    prepared.consistency_level = prepared1.consistency_level = prepared2.consistency_level = Consist_Level

    print( "query built and prepared")
    
    try: days = int(sys.argv[1])
    except: days = 1
    entriesPerDay = 100000
    
    # example async insert into table
    for day in range(days):
        for entry in range(entriesPerDay):
            build = []
            for x in range(len(labels)):
                build.append(generate(labels[x][0], labels[x][1], counts[x]))
            (session.execute_async( prepared.bind(build)))
            (session.execute_async( prepared1.bind(build)))
            (session.execute_async( prepared2.bind(build[:len(build)/2])))
        datadate += 86400 #increment one day 
            
    session.execute_async("create index on cdr (MONTH_DAY)")
    session.execute_async("create index on cdr (MOBILE_ID_TYPE)")
    print str((timeit.default_timer() - start_time)/60), " minutes elapsed"
    print seed, "seed used", days, 'days generated'
    
