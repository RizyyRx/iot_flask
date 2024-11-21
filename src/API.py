from mongogettersetter import MongoGetterSetter
from src.Database import Database
from time import time
from uuid import uuid4


db = Database.get_connection()

class APICollection(metaclass=MongoGetterSetter):
    def __init__(self,id):
        self._collection = db.sessions
        self._filter_query = {"id":id}

# when API object is created in register_api_key, it inherits the behavior defined by the metaclass MongoGetterSetter.
class API:
    def __init__(self,id):
        self.id = id
        self.collection = APICollection(id) # self.collection will have the getter/setter functionality defined in MongoGetterSetter

    def is_valid(self):
        login_time = self.collection.time
        validity = self.collection.validity
        if(validity == 0):
            return True
        now = time()
        return now - login_time < validity
        # ifnow - login_time < validity
        #     return True
        # else:
        #     return False

    
    # registers api key entry in session collection on db with _type='api'
    @staticmethod
    def register_api_key(session, name, group, remarks, request=None, validity=0, _type="api"):
        if not session.get('authenticated') or not session.get('username'):
            raise Exception("User not authenticated")
        uuid = str(uuid4())
        collection = db.sessions
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

        return uuid # This uuid is the api key