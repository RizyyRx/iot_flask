import json
import hashlib
from datetime import datetime, timedelta

def mask(str, length=6):
    visible = str[:length]
    hidden = "***"
    return visible + hidden

def time_ago(timestamp):
    now = datetime.now()
    time_difference = now - datetime.fromtimestamp(timestamp)

    # Calculate days, hours, and minutes
    days = time_difference.days
    seconds = time_difference.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Determine the appropriate time unit to display
    if days > 0:
        return f"{days} days ago"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return "Just now"


def check():
    print("working good....")

def get_config(key):
    config_file = "/home/rizwankendo/flask_config.json"
    file = open(config_file,"r")
    config = json.load(file) # json load converts json data to python dictionary
    file.close() # close file after reading

    if key in config:
        return config[key]
    else:
        raise Exception("The key {} is not found in config.json",format(key))

def md5_hash(string):
    hash_object = hashlib.md5(string.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex
