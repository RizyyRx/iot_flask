from flask import Blueprint, redirect, url_for, request, render_template, session
from src.User import User
from src.API import API
from src.Device import Device
from src.devices.MotionCamera import MotionCamera
from gridfs import GridFS, GridFSBucket
from src.Database import Database
import mimetypes
import uuid


bp = Blueprint("motion",__name__,url_prefix="/api/motion")

@bp.route("/capture", methods=['POST'])
def capture_motion():
    # The application accesses the file from the files dictionary on the request object.
    if 'file' in request.files and session['authenticated']:
        auth_header = request.headers.get('Authorization')
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
            mc.save_capture(file_id)
            return {
                'message': "Upload Success",
                'file_id': str(file_id),
                'filename': filename,
                'download_url': '/files/download/'+filename,
                'stream_url': '/files/stream/'+filename,
                'get_url': '/files/get/'+filename,
                'type': 'success'
            }, 200
    else:
        return{
            'message':'bad request'
        }, 400
    
