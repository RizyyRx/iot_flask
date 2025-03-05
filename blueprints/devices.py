from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from src.User import User
from src.Session import Session
from src.devices.MotionCamera import MotionCamera
from src.API import API
from src.Database import Database
from src.Device import Device
from src import get_config
from bson import ObjectId
import math
bp = Blueprint("devices", __name__, url_prefix="/devices")

@bp.route("/")
def devices_home():
    if not session.get('authenticated') or not session.get('username'):
            raise Exception("not authenticated")
    devices = Device.get_devices(session.get("username"))
    return render_template('devices.html', session=session, devices=devices)

@bp.route("/mcamera/<id>",methods=["GET", "POST"])
def devices_mcamera(id):
    dev = MotionCamera(id)
    db = Database.get_connection()

     # Handle device settings update when form is submitted
    if request.method == "POST":
        camera_status = request.form.get("camera_status")
        sleep_time = request.form.get("sleep_time")

        if not camera_status:
            return jsonify({"error": "Camera status is required"}), 400

        # Prepare update fields
        update_fields = {"device_status": camera_status}
        if sleep_time:
            update_fields["sleep_time"] = int(sleep_time)

        # Update the database
        update_result = db.devices.update_one(
            {"id": id, "user": session.get('username')},
            {"$set": update_fields}
        )

        if update_result.matched_count == 0:
            return jsonify({"error": "Device not found"}), 404

    # Fetch the first set of images (6 images or fewer if less than 6 are available)
    result = db.motion_capture.find({
        "device_id": id,
        "owner": session.get('username')
    }).sort([("time", -1)]).limit(6)

    # Create a list of image URLs and include the _id for pagination
    image_urls = [{'url': image['faccess']['get_url'], '_id': str(image['_id'])} for image in result]

    # Check if there are more images for the next query
    if len(image_urls) == 6:
        next_id = image_urls[-1]['_id']
    else:
        next_id = None  # No more images left

    # Render the template with the initial set of images and next_id
    return render_template('devices/mcamera.html', device=dev, images=image_urls, next_id=next_id)


@bp.route('/images/')
@bp.route('/images/<int:page>')
def gallery(page=1):
    db = Database.get_connection()
    images_per_page = 10
    skip = (page - 1) * images_per_page
    
    # Fetch the latest 10 images from MongoDB
    images = db.motion_capture.find().sort([('_id', -1)]).skip(skip).limit(images_per_page)

    # Get total number of images and calculate total pages
    total_images = db.motion_capture.count_documents({})
    total_pages = math.ceil(total_images / images_per_page)

    # Create image URLs with pagination
    image_urls = [{'url': image['faccess']['get_url'], '_id': str(image['_id'])} for image in images]

    return render_template('images.html', images=image_urls, page=page, total_pages=total_pages)

@bp.route("/add")
def devices_add():
    return render_template('devices/add.html', session=session, apis=API.get_all_keys(session, True), dtypes=get_config('devices'))
