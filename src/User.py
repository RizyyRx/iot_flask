from src.Database import Database
from src import get_config
from time import time
from random import randint
import binascii
import bcrypt

db = Database.get_connection()
users = db.users # create a collection of users if it doesnt exists

class User:
    def __init__(self, id):
        print("Initialized user with id:{}",format(id))
        #TODO: build user object if user is available

    @staticmethod
    def register(username, password, confirm_password):
        #TODO: avoid duplicate signups
        if password != confirm_password:
            raise Exception("passwords do not match")
        
        password = password.encode() # encode pass before hashing
        salt = bcrypt.gensalt() # generates salt
        hashed_pass = bcrypt.hashpw(password,salt) # hashes password with salt

        id = users.insert_one({
            "username":username, #TODO: make it as unique to avoid duplicate entries
            "password":hashed_pass,
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

            # #this method of checking pass is very insecure
            # if result['password'] == password: # alternate way: result.get('password') == password
            #     return True
            # else:
            #     #TODO: use sessions for additional security
            #     raise Exception("password is wrong")

            hashed_pass=result['password']
            
            if bcrypt.checkpw(password.encode(),hashed_pass):
                #TODO: register a session and return a session id on successful login
                return True
            else:
                #TODO: use sessions for additional security
                raise Exception("password is wrong")
        else:
            raise Exception("username is wrong")