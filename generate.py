import ast
import cassandra
from cassandra.cluster import Cluster
import random, sys
import string
import timeit
import uuid
import subprocess 

def randword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

acluster = 0
datadate = 1385305327 #equal to 2013-11-24 08:02:07-0700
session = None
def generate(label, element_type, frequency):
    global acluster
    global session
    global datadate
    """ Generate an element value to insert. of arbitrary type, which is a null
    value (1000-frequency)/1000 of the time
    """
    return random.randint(0, 9900000)
    if (random.randint(0, 1000) <= frequency):
        # column-specific data
        if (label == "MOBILE_ID_TYPE"):  # pretend this is partition by cluster
            result = acluster % 8
            session.execute_async(
                    session.prepare("update group_by_MOBILE_ID_TYPE set count = count + 1  where MOBILE_ID_TYPE = ? and id = 1")
                    .bind([result]))
            acluster += 1
        elif (label == "MONTH_DAY"):
            result = random.randint(1, 31)
            session.execute_async(
                    session.prepare("update group_by_month set count = count + 1  where MONTH_DAY = ? and id = 1")
                    .bind([result]))
        elif (label == "LONGITUDE" or label == "LAST_LONGITUDE"):
            result = random.random() * 360 - 180
        elif (label == "LATITUDE" or label == "LAST_LATITUDE"):
            result = random.random() * 180 - 90
        # type-specific fallback data
        elif (element_type == "float"):
            result = random.random()
        elif (element_type == "uuid"):
            result = uuid.uuid4()
            print result
        elif (element_type == "text"):
            result = randword(16)
        elif (element_type == "timestamp"):
            result = datadate
        else:
            result = random.randint(0, 9900000)
    else:
        result = ""
    return result

if __name__ == '__main__':
    start_time = timeit.default_timer()
    cluster = Cluster(['10.0.0.31', '10.0.0.38', '127.0.0.1'], port=9233)
    session = cluster.connect()  # keyspace should be our own
     
    print cluster.metadata.cluster_name
    print cassandra.__version__ +"\n"
    seed = 3333
    try:
        seed = int(sys.argv[2])
        random.seed(seed)
        session.execute("use group3")
    except: 
        session.execute("drop keyspace if exists group3", timeout=None)
        session.execute("CREATE KEYSPACE group3 WITH REPLICATION = { 'class' : 'SimpleStrategy','replication_factor' : 1 }",timeout=None)
        session.execute("use group3",timeout=None)
        random.seed(seed)
        with open("tableColumns.sql") as tables_setup:
            cols = tables_setup.read()
            for setupcmd in ["CREATE TABLE cdr(" + cols + """primary key(MSC_CODE ,CITY_ID,SERVICE_NODE_ID,RUM_DATA_NUM ,
                                MONTH_DAY ,DUP_SEQ_NUM ,MOBILE_ID_TYPE ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,
                                CON_OHM_NUM,SEIZ_CELL_NUM_L)) with clustering order by (city_id asc)"""
                             ,"CREATE TABLE query3(" + cols + """primary key(MSC_CODE ,DUP_SEQ_NUM ,CITY_ID,SERVICE_NODE_ID,RUM_DATA_NUM ,
                                MONTH_DAY ,MOBILE_ID_TYPE ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,
                                CON_OHM_NUM,SEIZ_CELL_NUM_L)) with clustering order by (DUP_SEQ_NUM asc)"""
                              ,"Create table group_by_month (id int, MONTH_DAY int, count counter, primary key (id,month_day)) with clustering order by (month_day asc)"
                              ,"Create table group_by_MOBILE_ID_TYPE (id int,MOBILE_ID_TYPE int, count counter, primary key (id,MOBILE_ID_TYPE))with clustering order by (mobile_id_type asc)"
                              , "create index on cdr (month_day)", "create index on cdr (MOBILE_ID_TYPE)"]:
                try:
                    session.execute(setupcmd, timeout=None)
                except Exception as error:
                    print error
    # read table stuffs from sample table schema
    with open("tableFrequency.txt") as tables_freq:
        (labels) = tables_freq.readlines()[0]
    labels = ast.literal_eval(labels)  # turn input into list correctly
    days = 1
    entriesPerDay = 10000
    try:
        if int(sys.argv[1]) >= 1:
            days = int(sys.argv[1])
    except:
        pass
    cdr = subprocess.Popen(["/$HOME/Documents/apache-cassandra-2.0.6/bin/cqlsh "+" localhost "+ " 9133 "+" -k "+" group3"],
                        stdin = subprocess.PIPE, stdout = subprocess.PIPE, shell=True)
    cdr.stdin.write("COPY cdr FROM STDIN;\n")
    
    for x in range(len(labels)):
        print labels[x][0], labels[x][1]
                #datadate += 86400 #increment one day
#     for i in range(days):
#         for k in range(entriesPerDay):
#             for x in range(len(labels)):
#                 gen = str(generate(labels[x][0], labels[x][1], 1000))
#                 if x < len(labels)-1:
#                     gen += ","
#                 cdr.stdin.write(gen)
#             cdr.stdin.write("\n")
#     cdr.stdin.write("\.\n")
#     cdr.stdin.close()
#     cdr.wait()

 
    print str((timeit.default_timer() - start_time)/60), " minutes elapsed"
    print seed, "seed used", days, 'days generated'
