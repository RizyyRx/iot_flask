from flask import Blueprint, render_template, redirect, url_for, request, session
from src.User import User
from src.Session import Session
from src.devices.MotionCamera import MotionCamera
from src.API import API
from src.Database import Database
from src.Device import Device
from src import get_config
bp = Blueprint("devices", __name__, url_prefix="/devices")

@bp.route("/")
def devices_home():
    devices = Device.get_devices()
    return render_template('devices.html', session=session, devices=devices)

@bp.route("/mcamera/<id>")  # css for this endpoint is not loading correctly, so I used static dir and link the css into there
def devices_mcamera(id):
    dev = MotionCamera(id)
    db = Database.get_connection()

    # Fetch all motion capture records for the device and user
    result = db.motion_capture.find({
        "device_id": id,
        "owner": session.get('username')
    }).sort([
        ("time", -1)
    ])

    # Create a list of image URLs to be passed to the template
    image_urls = [{'url': image['faccess']['get_url']} for image in result]  # Use 'result' here, not 'images'

    # Check if there are any images; if so, get the latest
    latest = image_urls[0]['url'] if image_urls else None

    return render_template('devices/mcamera.html', device=dev, latest=latest, images=image_urls)



# @bp.route("/mcamera/<id>/next_images/<start_index>")
# def fetch_more_images(id, start_index):
#     dev = MotionCamera(id)
#     db = Database.get_connection()

#     # Convert start_index to integer
#     start_index = int(start_index)

#     # Fetch the next 6 images, skipping the images before the start_index
#     result = db.motion_capture.find({
#         "device_id": id,
#         "owner": session.get('username')
#     }).sort([("time", -1)]).skip(start_index).limit(6)

#     # Check if images exist and extract URLs
#     image_urls = [{'url': image['faccess']['get_url']} for image in result]

#     # Return the images as JSON response
#     return jsonify(image_urls)



@bp.route("/add")
def devices_add():
    return render_template('devices/add.html', session=session, apis=API.get_all_keys(session, True), dtypes=get_config('devices'))
