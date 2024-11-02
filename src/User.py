from src.Database import Database
from src import get_config
from time import time
from random import randint

db = Database.get_connection()
users = db.users # create a collection of users if it doesnt exists

class User:
    def __init__(self, id):
        print("Initialized user with id:{}",format(id))
        #TODO: build user object if user is available

    @staticmethod
    def register(username, password, confirm_password):
        if password != confirm_password:
            raise Exception("passwords do not match")

        id = users.insert_one({
            "username":username,
            "password":password,
            "registered_time":time(),
            "active": False,
            "activate_token": randint(10000,99999)
        })

        # TODO: send the otp (activate_token) to user thru email or sms  
        return id
    
    @staticmethod
    def login(username, password):
        result = users.find_one({
            "username":username
        })

        if result:

            #this method of checking pass is very insecure
            if result['password'] == password: # alternate way: result.get('password') == password
                return True
            else:
                #TODO: use sessions for additional security
                raise Exception("password is wrong")
        else:
            raise Exception("username is wrong")