from src import get_config
from src.User import User

# uid = User.register("rizwan","yep123","yep123")

result = User.login("rizwan","yep123")

if result:
    print("login success")
else:
    print("login failed")