from src import get_config
from src.User import User

# uid = User.register("rizwan","yep123","yep123")
# print(uid)

try:
    result = User.login("rizwan","yep1234")
    if result:
        print("login success")
except Exception as e:
    print("login failed",e)