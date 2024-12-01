from flask import Blueprint, render_template, redirect, url_for, request, session
from src.User import User
from src.Session import Session
from src.API import API
from src.Device import Device
from src import get_config
bp = Blueprint("devices", __name__, url_prefix="/devices")

@bp.route("/")
def devices_home():
    devices = Device.get_devices()
    return render_template('devices.html', session=session, devices=devices)

@bp.route("/mcamera/<id>")
def devices_mcamera(id):
    pass

@bp.route("/add")
def devices_add():
    return render_template('devices/add.html', session=session, apis=API.get_all_keys(session, True), dtypes=get_config('devices'))
