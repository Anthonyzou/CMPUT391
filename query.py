import cassandra
from cassandra.cluster import SimpleStatement, Cluster
import timeit,sys

cluster = Cluster(['10.1.0.104', '10.1.0.105', '127.0.0.1'], port=9233)
cluster.default_timeout = None
session = cluster.connect('group3alt')  # keyspace should be our own

indexsearch = False #turn this to true when you want to do looping queries for group by

print cluster.metadata.cluster_name  # should make sure this is group3
print cassandra.__version__,"\n"

try: Consist_Level = int(sys.argv[1])
except: Consist_Level = 1

program_st = timeit.default_timer()
#======================================================================
# QUERY 1
#======================================================================
query = SimpleStatement("""
SELECT count (*) as ten_atomic
FROM cdr 
WHERE 
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
> (10000,10000,10000,3,10000,1,10000,10000,10000,10000)
AND (MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
< (150000,150000,150000,30,150000,6,150000,150000,150000,150000)
LIMIT 4000
ALLOW FILTERING ; 
""",consistency_level=Consist_Level)
start_time = timeit.default_timer()
print session.execute(query,timeout = None)[0]

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 1\n"

#======================================================================
# QUERY 1 alternative
#======================================================================
query = SimpleStatement("""
SELECT count (*) as ten_atomic
FROM cdr_alt 
WHERE 
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
> (10000,10000,10000,3,10000,1,10000,10000,10000,10000)
AND (MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
< (150000,150000,150000,30,150000,6,150000,150000,150000,150000)
LIMIT 4000
ALLOW FILTERING ; 
""",consistency_level=Consist_Level)
start_time = timeit.default_timer()
print session.execute(query,timeout = None)[0]

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 1\n"
#======================================================================
# QUERY 1 small
#======================================================================
query = SimpleStatement("""
SELECT count (*) as ten_atomic
FROM smallcdr 
WHERE 
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
> (10000,10000,10000,3,10000,1,10000,10000,10000,10000)
AND (MSC_CODE ,CITY_ID,SERVICE_NODE_ID
,RUM_DATA_NUM ,DUP_SEQ_NUM ,SEIZ_CELL_NUM ,FLOW_DATA_INC ,SUB_HOME_INT_PRI ,CON_OHM_NUM,
SESS_SFC) 
< (150000,150000,150000,30,150000,6,150000,150000,150000,150000)
LIMIT 4000
ALLOW FILTERING ; 
""",consistency_level=Consist_Level)
start_time = timeit.default_timer()
print session.execute(query,timeout = None)[0]

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 1\n"

#======================================================================
# QUERY 2
#======================================================================
query = SimpleStatement(""" 
SELECT count (*) as range_city_id
FROM cdr
WHERE
MSC_CODE > 5000 AND MSC_CODE < 90000
LIMIT 4000
ALLOW FILTERING;
""",consistency_level=Consist_Level)
start_time = timeit.default_timer()
print (session.execute(query, timeout=None)[0])
print str((timeit.default_timer() - start_time)/60), " minutes elapsed for query 2\n"
#======================================================================
# QUERY 3
#======================================================================
query = SimpleStatement("""
SELECT count(*) as range_DUP_SEQ_NUM
FROM cdr
WHERE 
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID,RUM_DATA_NUM ,DUP_SEQ_NUM )
>(0,0,0,0,10000) AND
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID ,RUM_DATA_NUM ,DUP_SEQ_NUM)
<(9900,9900,9900,9900,30000)
LIMIT 4000
ALLOW FILTERING;
""",consistency_level=Consist_Level)
start_time = timeit.default_timer()
print session.execute(query,timeout=None)[0]

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 3\n"
#======================================================================
# QUERY 4
#======================================================================
start_time = timeit.default_timer()
prep = session.prepare("select count(*) from group_by_MOBILE_ID_TYPE where MOBILE_ID_TYPE = ?")
prep.consistency_level = Consist_Level

for i in range (8):
    print str(i) + " : " , session.execute(prep.bind([i]),timeout=None)
print str((timeit.default_timer() - start_time)) + " seconds elapsed for query 4 loop\n"
#======================================================================
# QUERY 4
#======================================================================
if indexsearch:
    start_time = timeit.default_timer()
    prep = session.prepare("select count(*) from cdr where MOBILE_ID_TYPE = ?")
    prep.consistency_level = 1
    for i in range (8):
        print str(i) + " : " , session.execute(prep.bind([i]),timeout=None)
    print str((timeit.default_timer() - start_time)) + " seconds elapsed for query 4 loop on cdr index\n"

#======================================================================
# QUERY 5
#======================================================================
start_time = timeit.default_timer()
prep = session.prepare("select count(*) from group_by_month where month_day = ?")
prep.consistency_level = Consist_Level
for i in range (1,32):
    print str(i) + " : " , session.execute(prep.bind([i]), timeout=None)
print str((timeit.default_timer() - start_time)) + " seconds elapsed for query 5 loop\n"
#======================================================================
# QUERY 5
#======================================================================
if indexsearch:
    start_time = timeit.default_timer()
    prep = session.prepare("select count(*) from cdr where month_day = ?")
    prep.consistency_level = 1
    for i in range (1,32):
        print str(i) + " : " , session.execute(prep.bind([i]), timeout=None)
    print str((timeit.default_timer() - start_time)) + " seconds elapsed for query 5 loop on cdr index\n"

print str((timeit.default_timer() - program_st)/60)+ " minutes elapsed for program\n"
