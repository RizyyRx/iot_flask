from flask import Flask, redirect, url_for, request, render_template
import os
import math

app = Flask(__name__) #app is an object being created of class Flask
basename = '/iot' #use a base dir if needed and add it to app route

@app.route(basename+'/') #decorator that binds url with a function
def hello_world():
   return render_template('helloworld.html')   

@app.route(basename+'/dashboard')
def dashboard():
   return render_template('dashboard.html') #render template automatically looks for dir named templates and loads respective files from it

#runs whoami linux cmd and displays output (note that the output contains \n at the end of the string)
@app.route(basename+'/whoami')
def whoami():
   return os.popen('whoami').read()

if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)