from pymongo import MongoClient
    
# connect to db    
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["rizyy_iot"]

    if db is not None:
        print("Connected successfully")
    else:
        print("Not connected")
except Exception as e:
    print(f"Error: {e}")
    
result = db.devices.find_one({"user":"rizwan"})
print(result)