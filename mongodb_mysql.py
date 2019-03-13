import pymongo
import pprint
from pymongo import MongoClient

client = MongoClient()

# Get the sam logs db
db = client.sam_logs_2017_12_18

#Get the db collections
edge_collection = db.edges
node_collection = db.nodes

pprint.pprint(edge_collection.find_one())
