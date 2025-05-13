from mongogettersetter import MongoGetterSetter
from src.Database import Database
from uuid import uuid4
from time import time
from src.API import API

db = Database.get_connection()

class DeviceCollection(metaclass=MongoGetterSetter):
    def __init__(self, id):
        self._collection = db.devices
        self._filter_query = {
            '$or': [
                {'id': id},
            ]
        }
        
class Device:
    def __init__(self, id):
        self.collection = DeviceCollection(id)
        self.id = self.collection.id
    
    def delete():
        api = API(self.collection.api)
        api.collection.linked_device = None
        self.collection.delete()
        
    @staticmethod
    def register_device(name, username, _type, api_key, remarks):
        uuid = str(uuid4())
        
        #Link the device to API
        api = API(api_key)
        api.collection.linked_device = uuid
        
        collection = db.devices
        result = collection.insert_one({
            "id": uuid,
            "user": username,
            "name": name,
            "remarks": remarks,
            "group": api.collection.group,
            "type": _type,
            "active": True,
            "registered_on": time(),
            "api": api_key,
            "last_seen": None,
            "device_status":"on",
            "sleep_time": None,
            "ai_mode": "off",
            "face_detection_sleep_time": None,
            "sleep_on_face_detection": "no",
            "chat_id":None,
            "bot_token":None
        })
        
        return Device(uuid)
    
    @staticmethod
    def get_devices(username):
        collection = db.devices
        return collection.find({"user":username})

    @staticmethod
    def get_devices_count(session):
        if  session.get('authenticated') or  session.get('username'):
       
            username = session.get("username")
            collection = db.devices
            return collection.count_documents({"user":username})

