from flask import Blueprint, redirect, url_for, request, render_template, session
from src.User import User
from src.API import API
from src.Device import Device
from src.devices.MotionCamera import MotionCamera
from gridfs import GridFS, GridFSBucket
from src.Database import Database
import mimetypes
import uuid
import threading


bp = Blueprint("motion",__name__,url_prefix="/api/motion")
db = Database.get_connection()

@bp.route("/capture", methods=['POST'])
def capture_motion():
    if 'file' in request.files and session.get('authenticated'):
        auth_header = request.headers.get('X-Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
            print(auth_token)
            api = API(auth_token)
            device = api.get_device()  
            device_id = device['id']
            file = request.files['file']
            fs = GridFSBucket(Database.get_connection())
            
            metadata = {
                'original_filename': file.filename,
                'content_type': mimetypes.guess_type(file.filename)[0],
                'owner': session.get('username'),
                'device_id': device_id
            }
            
            filename = str(uuid.uuid4())
            
            file_id = fs.upload_from_stream(filename, file, metadata=metadata)
            mc = MotionCamera(device_id)

            result = db.devices.find_one({"user":session.get("username"),"id":device_id})
            bot_token=result["bot_token"]
            chat_id=result["chat_id"]
            print(f"aimode_status:{result["ai_mode"]}")

            if result["ai_mode"] == "on":
                if result["sleep_on_face_detection"] == "yes":
                    sleep_on_face_detection_status = "yes"
                else:
                    sleep_on_face_detection_status = "no"
                face_detection_sleep_time=result["face_detection_sleep_time"]
                username = str(session.get("username"))

                # Run face check in a background thread
                threading.Thread(target=API.compare_faces, args=(file_id, fs, username, device_id, sleep_on_face_detection_status, face_detection_sleep_time)).start()
            else:
                print("ai mode is off, not running face check")

            faccess = {
                'message': "Upload Success",
                'file_id': str(file_id),
                'filename': filename,
                'download_url': '/files/download/'+filename,
                'stream_url': '/files/stream/'+filename,
                'get_url': '/files/get/'+filename,
                'type': 'success'
            }
            mc.save_capture(file_id, faccess)
            if bot_token and chat_id:
                API.send_telegram_alert(bot_token=bot_token, chat_id=chat_id)
            return faccess, 200
    else:
        return {
            'message': 'Bad Request',
            'type': 'error'
        }, 400

    
@bp.route('/latest/<id>')
def latest_motion_capture(id):
    db = Database.get_connection()
    result = db.motion_capture.find_one({
        "device_id": id,
        "owner": session.get('username')
    }, sort=[
        ("time", -1)
    ])

    if result:
        return {
            "uri": result['faccess']['get_url']
        }
    else:
        return {
            "error": "Cannot find"
        }
