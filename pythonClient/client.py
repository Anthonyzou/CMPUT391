from cassandra.cluster import Cluster
import random
from random import randint
from xmlrpclib import MAXINT, MININT

cluster = Cluster( ['199.116.235.57',
                    '10.0.0.31',
                    '10.0.0.38',
                    '127.0.0.1'
                    ])

session = cluster.connect('group3') #keyspace should be our own

metadata = cluster.metadata
print metadata.cluster_name #should make sure this is group3

random.seed(3333)

query = "drop table users"
session.execute(query)
query = """CREATE TABLE users (
           id int PRIMARY KEY,
           name int,
           age int)"""
session.execute(query)


query = "INSERT INTO users (id, name, age) VALUES (?, ?, ?)" 
prepared = session.prepare(query)
 
#example async insert into table.


for y in range(10):
    build = []
    for x in range(3):
        build.append((randint(1,MAXINT)))
    bound = (prepared.bind(build) )
    session.execute_async(bound)

    