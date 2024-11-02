from src.Database import Database
from src import get_config

class User:
    def __init__(self, id):
        print("Initialized user with id:{}",format(id))
        db = Database.get_connection()
        print(list(db.users.find()))