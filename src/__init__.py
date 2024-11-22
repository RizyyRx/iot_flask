import json
import hashlib


def check():
    print("working good....")

def get_config(key):
    config_file = "/home/rizwankendo/flask/config.json"
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
