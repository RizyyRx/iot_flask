from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash
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
    #fetching all devices with current username
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
        ai_mode = request.form.get("ai_mode")
        sleep_on_face_detection = request.form.get("sleep_on_face_detection")
        face_detection_sleep_time = request.form.get("face_detection_sleep_time")

        if not camera_status:
            return jsonify({"error": "Camera status is required"}), 400

        # Prepare update fields dynamically
        update_fields = {}
        
        if camera_status:
            update_fields["device_status"] = camera_status
        if ai_mode:
            update_fields["ai_mode"] = ai_mode
        if sleep_on_face_detection:
            update_fields["sleep_on_face_detection"] = sleep_on_face_detection
        if sleep_time:
            update_fields["sleep_time"] = int(sleep_time)
        if face_detection_sleep_time:
            update_fields["face_detection_sleep_time"] = int(face_detection_sleep_time)

        # Only update the database if there are fields to update
        if update_fields:
            update_result = db.devices.update_one(
                {"id": id, "user": session.get('username')},
                {"$set": update_fields}
            )

            if update_result.matched_count == 0:
                return jsonify({"error": "Device not found"}), 404
        
    device_settings_result = db.devices.find_one({"user":session.get("username"),"id":id})
    device_status = device_settings_result["device_status"]
    ai_mode_status = device_settings_result["ai_mode"]
    sleep_time_value = device_settings_result["sleep_time"] 
    sleep_on_face_detection_status = device_settings_result["sleep_on_face_detection"]
    bot_token = device_settings_result["bot_token"]
    chat_id= device_settings_result["chat_id"]


    # Fetch the first set of images (6 images or fewer if less than 6 are available)
    print(id)
    print(f"username: {session.get('username')}")
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
    return render_template('devices/mcamera.html', device_id=id, device=dev, images=image_urls, next_id=next_id, device_status=device_status, ai_mode_status=ai_mode_status,sleep_time_value=sleep_time_value, sleep_on_face_detection_status=sleep_on_face_detection_status,bot_token=bot_token,chat_id=chat_id)


@bp.route('/images/<device_id>')
@bp.route('/images/<device_id>/<int:page>')
def gallery(device_id,page=1):
    db = Database.get_connection()
    username = session.get('username')
    images_per_page = 10
    skip = (page - 1) * images_per_page

    # Filter images by device_id and username
    query = {
        "device_id": device_id,
        "owner": username
    }
    
    # Fetch the latest 10 images from MongoDB
    images = db.motion_capture.find(query).sort([('_id', -1)]).skip(skip).limit(images_per_page)

    # Get total number of images and calculate total pages
    total_images = db.motion_capture.count_documents({})
    total_pages = math.ceil(total_images / images_per_page)

    # Create image URLs with pagination
    image_urls = [{'url': image['faccess']['get_url'], '_id': str(image['_id'])} for image in images]

    return render_template('images.html', images=image_urls, page=page, total_pages=total_pages,device_id=device_id)

@bp.route("/delete_images/<device_id>", methods=["POST"])
def delete_all_images(device_id):
    db = Database.get_connection()
    username = session.get('username')

    # Delete all images belonging to this device and user
    db.motion_capture.delete_many({
        "device_id": device_id,
        "owner": username
    })
    return redirect(url_for("devices.devices_mcamera", id=device_id))

@bp.route('/update_bot_config/<device_id>', methods=['POST'])
def update_bot_config(device_id):
    bot_token = request.form.get("bot_token")
    chat_id = request.form.get("chat_id")
    username = session.get("username")

    db = Database.get_connection()

    # Update user config for this specific device
    db.devices.update_one(
        {"user": username, "id": device_id},
        {"$set": {
            "bot_token": bot_token,
            "chat_id": chat_id
        }}
    )
    return redirect(url_for("devices.devices_mcamera", id=device_id))

@bp.route("/remove_device/<device_id>", methods=["POST"])
def remove_device(device_id):
    db = Database.get_connection()
    username = session.get("username")

    # Remove the device only if it belongs to the current user
    result = db.devices.delete_one({
        "id": device_id,
        "user": username
    })

    # Remove the device only if it belongs to the current user
    result = db.api_keys.update_one(
        {"username": username},
        {"$set": {
            "linked_device": None
        }}
        )

    return redirect(url_for("devices.devices_home"))


@bp.route("/add")
def devices_add():
    return render_template('devices/add.html', session=session, apis=API.get_all_keys(session, True), dtypes=get_config('devices'))
