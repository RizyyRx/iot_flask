from src.User import User
from src.Session import Session
from src.Group import Group
from src.API import API, APICollection
from flask import Blueprint, redirect, url_for, request, render_template, session

bp = Blueprint("apiv1",__name__,url_prefix="/api/v1")

@bp.route("/create/key",methods=['POST'])
def create_api_key():
   name = request.form['name']
   group = request.form['group']
   remarks = request.form['remarks']

   if session.get('authenticated'):
      a = API.register_api_key(session, name, group, remarks)
      return{
         "key": str(a.collection.id),
         "hash": str(a.collection.hash),
         "message":"success"
      }, 200
   else:
      return{
         "message":"not authenticated"
      }, 401

@bp.route("/create/group",methods=['POST'])
def create_group():
   name = request.form['name']
   description = request.form['description']

   if(len(name) < 3) or (len(description) < 3):
      return {
         "message": "Name and Description must be atleast 3 characters",
      }, 400

   if session.get('authenticated'):
      Group.register_group(name, description)
      return{
         'status':"success",
         'message':'successfully created group ' + name
      }, 200
   else:
      return{
         'message':'not authenticated'
      }, 401


@bp.route('/register',methods=['POST'])
def register():
   if 'username' in request.form and 'password' in request.form and 'name' in request.form and 'email' in request.form:
      username = request.form['username']
      password = request.form['password']
      name = request.form['name']
      email = request.form['email']

      try:
         uid = User.register(username,password,password,name,email)
         return{
            "message": "Successfully Registered",
            "user_id": uid
         }, 200
      except Exception as e:
         return{
            "message": str(e),
         }, 400
   else:
      return {
         "message": "Not enough parameters",
      }, 400


@bp.route('/auth',methods=['POST'])
def auth():
   if session.get('authenticated'):
      print(session)
      sess = Session(session['sessid']) # create a session instance with sessid present in flask's session object
      if sess.is_valid():
         return{
            "message":"Already authenticated",
            "authenticated":True
         }, 202 #already authed
      else:
         session['authenticated'] = False # set authenticated to false in flask session object
         sess.collection.active = False # set active to false directly in db since sess inherits the mongogettersetter metaclass and sess.collection will have the session collection
         return{
            "message":"Session expired",
            "authenticated":False
         }, 401
   else: 
      if 'username' in request.form and 'password' in request.form:
         username = request.form['username']
         password = request.form['password']
         try:
            sessid = User.login(username,password) # sessid is retrieved here from the Session object created while registering session
            #These are flask's session (session is flask's session object)
            session['authenticated'] = True
            session['username'] = username
            session['sessid'] = sessid

            if 'redirect' in request.form and request.form['redirect'] == 'true':
               return redirect(url_for('home.dashboard')) # if authed, redirect to dashboard page
            else:
               return{
                  "message":"authenticated successfully",
                  "authenticated":True,
                  # "session_id":sessid,
                  "username":username
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
      

@bp.route('/deauth')
def deauth():
   session['authenticated'] = False
   # return{
   #    "message":"successfully deauthed",
   #    "authenticated":False
   # }, 200
   return redirect(url_for('home.dashboard'))