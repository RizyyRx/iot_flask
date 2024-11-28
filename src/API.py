from mongogettersetter import MongoGetterSetter
from src.Database import Database
from time import time
from uuid import uuid4
from src import md5_hash


db = Database.get_connection()

class APICollection(metaclass=MongoGetterSetter):
    def __init__(self,id):
        self._collection = db.api_keys
        self._filter_query = {'$or': [
            {'id': id},
            {'hash': id}
        ]}

# when API object is created in register_api_key, it inherits the behavior defined by the metaclass MongoGetterSetter.
class API:
    def __init__(self,id):
        self.collection = APICollection(id) # self.collection will have the getter/setter functionality defined in MongoGetterSetter
        try:
            self.id = str(self.collection.id)
        except TypeError:
            raise Exception("API Key not found")

    def is_valid(self):
        login_time = self.collection.time
        validity = self.collection.validity
        if validity == 0:
            return self.collection.active # if validity is 0, just return if active is true or false
        else:
            if self.collection.active: #if validity is not 0 and active is true, check validity status
                now = time()
                return now - login_time < validity
            else: #if validity is not 0 and active is false, return false
                return False 
        
    #get all api keys registered by username 
    @staticmethod
    def get_all_keys(session):
        if not session.get('authenticated') or not session.get('username'):
            raise Exception("not authenticated")
        
        username = session.get("username")
        collection = db.api_keys
        result = collection.find({"username":username})
        return result
    
    # registers api key entry in session collection on db with _type='api'
    @staticmethod
    def register_api_key(session, name, group, remarks, request=None, validity=0, _type="api"):
        if not session.get('authenticated') or not session.get('username'):
            raise Exception("User not authenticated")
        uuid = str(uuid4())
        collection = db.api_keys
        username = session.get('username')

        if request is not None:
            request_info = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'data': request.get_data().decode('utf-8')
            }
        else:
            request_info = None

        result = collection.insert_one({
            "id":uuid,
            "hash": md5_hash(uuid),
            "username":username,
            "name":name,
            "group":group,
            "remarks":remarks,
            "time":time(),
            "validity":validity,
            "active":True,
            "type":_type,
            "request":request_info
        })

        return API(uuid) # This uuid is the api key