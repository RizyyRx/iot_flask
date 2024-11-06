from flask import Blueprint, redirect, url_for, request, render_template, session
from src.User import User

bp = Blueprint("apiv1",__name__,url_prefix="/api/v1")

@bp.route('/auth',methods=['POST'])
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
            # return{
            #    "message":"authenticated successfully",
            #    "authenticated":True
            # } , 200 # ok
            return redirect(url_for('home.dashboard')) # if authed, redirect to dashboard page
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
      

@bp.route('/deauth')
def deauth():
   session['authenticated'] = False
   # return{
   #    "message":"successfully deauthed",
   #    "authenticated":False
   # }, 200
   return redirect(url_for('home.dashboard'))