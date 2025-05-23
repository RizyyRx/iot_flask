from flask import Blueprint, redirect, url_for, request, render_template, session
from src.User import User
from src.Device import Device
from src.Group import Group
from src.API import API
from src import md5_hash, time_ago, mask

bp = Blueprint("home",__name__,url_prefix="/")

@bp.route("/")
def home():
    return render_template('home.html')

@bp.route('/dashboard')
def dashboard():
   keys_count = API.get_keys_count(session)
   device_count = Device.get_devices_count(session)
   images_count = API.get_images_count(session)
   return render_template('dashboard.html',session=session,keys_count=keys_count,device_count=device_count,images_count=images_count) #render template automatically looks for dir named templates and loads respective files from it

@bp.route('/signup')
def signup():
   return render_template('_signup.html') #render template automatically looks for dir named templates and loads respective files from it

@bp.route('/api_keys')
def api_keys():
   username = session.get('username')
   groups = list(Group.get_groups(username))
   api_keys = API.get_all_keys(session)
   return render_template('api_keys.html', session=session, api_keys=api_keys, groups=groups, time_ago=time_ago, mask=mask)

@bp.route("/api_keys/row")
def api_keys_row():
   username = session.get('username')
   api_key_hash = request.args.get('hash')
   print(api_key_hash)
   api = API(api_key_hash)
   print(api.collection._data)
   groups = Group.get_groups(username)
   return render_template('api_keys/row.html', key=api.collection._data, groups=groups, time_ago=time_ago, mask=mask)

@bp.route("/api_keys/enable", methods=['POST'])
def enable_api_key():
   api_key_hash = request.form['id']
   api_key_status = request.form['status']
   print(bool(api_key_status))
   api = API(api_key_hash)
   api.collection.active = api_key_status == "true"
   return {
      'status': api.collection.active
   }, 200

@bp.route("/api_keys/row/delete_dialog")
def api_keys_delete_dialog():
   api_key_hash = request.args.get('hash')
   api = API(api_key_hash)
   return render_template('dialogs/delete_api_key.html', key=api.collection._data, time_ago=time_ago, mask=mask)

@bp.route("/api_keys/row/delete")
def api_keys_delete():
   api_key_hash = request.args.get('hash')
   api = API(api_key_hash)
   api.delete()
   return {
      'status': 'success'
   }, 200
