import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://rizyy:password%40123@mongodb.selfmade.ninja/?authSource=users') # connect to client

db = client.rizyy_iot #connect to db

# result = db.users.update_one({"username":"riz"},{"$set":{"password":"321"}}) #update operation

result = db.users.find_one({"username":"riz"})

print(result)