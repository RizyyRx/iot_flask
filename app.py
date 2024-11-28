import sys
sys.path.append('/home/rizwankendo/flask') # this will help to find the app.py for deployment server 

from flask import Flask, redirect, url_for, request, render_template, session
import os
import math
from src import get_config
from src.User import User
from src.API import API
from blueprints import home, api, files, motion, dialogs

'''
 * by using static_folder='assets', static_url_path=basename, now all the contents inside assets will be available in the basename iot/ in website.
 * the assets dir is kept static
 * put application, coz wsgi looks for var named application by default that has the flask object
'''
application = app = Flask(__name__, static_folder='assets', static_url_path="/") #app is an object being created of class Flask  
app.secret_key = get_config("secret_key") # flask uses this key to auth session


@app.before_request
def before_request_hook():
   if session.get('type') == 'web': # leave if the session type is web, this check is only for api keys
      return
   
   auth_header = request.headers.get('Authorization')
   if auth_header:
      auth_token = auth_header.split(" ")[1]
      try:
         api = API(auth_token)
         session['authenticated'] = api.is_valid() # if is valid, then auth is true
         session['username'] = api.collection.username
         session['type'] = 'api'
         session['sessid'] = None
      except Exception as e:
         return "Unauthorized" + str(e), 401

   else:
      session['authenticated'] = False
      if 'username' in session:
         del session['username']

app.register_blueprint(home.bp)
app.register_blueprint(api.bp)
app.register_blueprint(files.bp)
app.register_blueprint(motion.bp)
app.register_blueprint(dialogs.bp)

if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)