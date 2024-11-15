from mongogettersetter import MongoGetterSetter
from src.Database import Database

db = Database.get_connection()

class SessionCollection(metaclass=MongoGetterSetter):
    def __init__(self,id):
        self._collection = db.sessions
        self._filter_query = {"id":id}

class Session:
    def __init__(self,id):
        self.id = id
        self.collection = SessionCollection(id)

sess = Session("uuid here")