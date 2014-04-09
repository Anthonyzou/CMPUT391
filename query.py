import cassandra
from cassandra.cluster import Cluster
import timeit

cluster = Cluster(['10.0.0.70', '10.0.0.31', '10.0.0.38', '127.0.0.1'], port=9233)
cluster.default_timeout = None
session = cluster.connect('group3')  # keyspace should be our own

loop = False #turn this to true when you want to do looping queries for group by

print cluster.metadata.cluster_name  # should make sure this is group3
print cassandra.__version__,"\n"

program_st = timeit.default_timer()
#======================================================================
# QUERY 1
#======================================================================
query = """
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
LIMIT 40000000
ALLOW FILTERING ;
"""
start_time = timeit.default_timer()
print session.execute(query)[0]

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 1\n"
#======================================================================
# QUERY 2
#======================================================================
query = """ 
SELECT count (*) as range_city_id
FROM cdr
WHERE
MSC_CODE > 5000 AND MSC_CODE < 90000
LIMIT 40000000
ALLOW FILTERING;
"""
start_time = timeit.default_timer()
print session.execute(query)[0]
print str((timeit.default_timer() - start_time)/60), " minutes elapsed for query 2\n"
#======================================================================
# QUERY 3
#======================================================================
query = """
SELECT count(*) as range_DUP_SEQ_NUM
FROM cdr
WHERE 
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID,RUM_DATA_NUM ,DUP_SEQ_NUM )
>(0,0,0,0,3000) AND
(MSC_CODE ,CITY_ID,SERVICE_NODE_ID ,RUM_DATA_NUM ,DUP_SEQ_NUM)
<(9900,9900,9900,9900,30000)
LIMIT 40000000
ALLOW FILTERING;
"""
start_time = timeit.default_timer()
temp = session.execute(query)[0]
print temp

print str((timeit.default_timer() - start_time) /60), " minutes elapsed for query 3\n"
#======================================================================
# QUERY 4
#======================================================================
query = """
SELECT MOBILE_ID_TYPE,count
from GROUP_BY_MOBILE_ID_TYPE
"""
start_time = timeit.default_timer()

for i in range (8):
    print str(i) + " : " , session.execute(session.prepare("select count(*) from group_by_MOBILE_ID_TYPE where MOBILE_ID_TYPE = ?").bind([i]))
print str((timeit.default_timer() - start_time)) + " seconds elapsed for query 4 loop\n"
#======================================================================
# QUERY 5
#======================================================================
query = """
SELECT month_day, count FROM group_by_month
"""
start_time = timeit.default_timer()

for i in range (1,31):
    print str(i) + " : " , session.execute(session.prepare("select count(*) from group_by_month where month_day = ?").bind([i]))

print str((timeit.default_timer() - program_st)/60)+ " minutes elapsed for program\n"
