from flask import Flask, redirect, url_for, request, render_template
import os
import math
from src import check
from src.User import User

check()

app = Flask(__name__) #app is an object being created of class Flask
basename = '/iot' #use a base dir if needed and add it to app route

@app.route(basename+'/') #decorator that binds url with a function
def hello_world():
   d={"username": whoami().strip(),"env": "wsl_kali"}
   return render_template('helloworld.html',data=d)

#runs whoami linux cmd and displays output (note that the output contains \n at the end of the string)
@app.route(basename+'/whoami')
def whoami():
   return os.popen('whoami').read()

if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)