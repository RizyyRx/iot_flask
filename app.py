from flask import Flask, redirect, url_for, request, render_template
import os
import math
from src import get_config

basename = get_config("basename") #use a base dir if needed and add it to app route
# by using static_folder='assets', static_url_path=basename, now all the contents inside assets will be available in the basename iot/ in website.
# the assets dir is kept static
app = Flask(__name__, static_folder='assets', static_url_path=basename) #app is an object being created of class Flask  

@app.route(basename+'/dashboard')
def dashboard():
   session = {
      "authenticated": True,
      "username": "riz"
   }
   return render_template('dashboard.html',session=session) #render template automatically looks for dir named templates and loads respective files from it


if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)