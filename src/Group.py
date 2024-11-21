from mongogettersetter import MongoGetterSetter
from src.Database import Database
from time import time
from uuid import uuid4

db = Database.get_connection()

class GroupCollection(metaclass=MongoGetterSetter):
    def __init__(self,id):
        self._collection = db.groups
        self._filter_query = {
            '$or':[
                {'id':id}, #filter either with id or name
                {'name':id}
            ]
        }

# when Group object is created in register_Group, it inherits the behavior defined by the metaclass MongoGetterSetter.
class Group:
    def __init__(self,id):
        self.collection = GroupCollection(id) # self.collection will have the getter/setter functionality defined in MongoGetterSetter
        self.id = self.collection.id

    @staticmethod
    def register_group(name, description):
        uuid = str(uuid4())
        collection = db.groups

        result = collection.insert_one({
            "id":uuid,
            "name":name,
            "description":description,
            "time":time(),
            "active":True,
        })

        return Group(uuid)

    @staticmethod
    def get_groups():
        collection = db.groups
        return collection.find({})
