SELECT count (*) as range_city_id
FROM cdr
WHERE
MSC_CODE > 5000 AND MSC_CODE < 90000
LIMIT 4000
ALLOW FILTERING;
