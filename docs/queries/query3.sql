SELECT count(*) as range_DUP_SEQ_NUM
FROM cdr
WHERE (CITY_ID, SERVICE_NODE_ID, RUM_DATA_NUM, MONTH_DAY, DUP_SEQ_NUM)
> (0, 0, 0, 0, 30000) 
AND
(CITY_ID, SERVICE_NODE_ID, RUM_DATA_NUM, MONTH_DAY, DUP_SEQ_NUM)
< (9900000, 9900000, 9900000, 9900000, 300000)
LIMIT 40000000
ALLOW FILTERING;
