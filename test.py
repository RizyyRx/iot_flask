from mongogettersetter import MongoGetterSetter
from src.Database import Database
from src.API import API, APICollection

db = Database.get_connection()

# class SessionCollection(metaclass=MongoGetterSetter):
#     def __init__(self,id):
#         self._collection = db.sessions
#         self._filter_query = {"id":id}

# class Session:
#     def __init__(self,id):
#         self.id = id
#         self.collection = SessionCollection(id)

# sess = Session("uuid here")

a = API("89712925-d766-482e-a133-638fedb8260d")
print(a.collection.active)