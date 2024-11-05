from flask import Flask, redirect, url_for, request, render_template, session
import os
import math
from src import get_config
from src.User import User

basename = get_config("basename") #use a base dir if needed and add it to app route
# by using static_folder='assets', static_url_path=basename, now all the contents inside assets will be available in the basename iot/ in website.
# the assets dir is kept static
app = Flask(__name__, static_folder='assets', static_url_path=basename) #app is an object being created of class Flask  
app.secret_key = get_config("secret_key") # flask uses this key to auth session

@app.route(basename+'/dashboard')
def dashboard():
   return render_template('dashboard.html',session=session) #render template automatically looks for dir named templates and loads respective files from it

@app.route(basename+'/auth',methods=['POST'])
def auth():
   if session.get('authenticated'):
      return{
         "message":"Already authenticated",
         "authenticated":True
      }, 202 #already authed
   else: 
      if 'username' in request.form and 'password' in request.form:
         username = request.form['username']
         password = request.form['password']
         try:
            User.login(username,password)
            session['authenticated'] = True
            return{
               "message":"authenticated successfully",
               "authenticated":True
            } , 200 # ok
         except Exception as e:
            return{
               "message":str(e),
               "authenticated":False
            }, 401 # not authed
      else:
         return{
            "message":"Not enough parameters",
            "authenticated":False
         }, 400 # bad request
      

@app.route(basename+'/deauth')
def deauth():
   session['authenticated'] = False
   return{
      "message":"successfully deauthed",
      "authenticated":False
   }, 200

if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)