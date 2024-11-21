from flask import Blueprint, redirect, url_for, request, render_template, session
from src.Database import Database
from gridfs import GridFS, GridFSBucket
import mimetypes
import uuid

bp = Blueprint("motion",__name__,url_prefix="/api/motion")

@bp.route("/capture", methods=['POST'])
def capture_motion():
    # The application accesses the file from the files dictionary on the request object.
    if 'file' in request.files and session['authenticated']:
        file = request.files['file']
        fs = GridFSBucket(Database.get_connection()) # create an instance of GridFSBucket with db connection
        original_filename = file.filename

        metadata = {
            'original_filename':original_filename,
            'content_type':mimetypes.guess_type(original_filename)[0], # creates file content type from file name
            'owner':session.get('username')
        } # give 0th index to only get the string of filetype from a list

        filename = str(uuid.uuid4()) # create a random string for file name for uploading to db

        file_id = fs.upload_from_stream(filename, file, metadata=metadata) #upload file to db (returns a file id)

        return{
            'message':"upload_success",
            'filename':filename,
            'file_id':str(file_id),
            'download_url':'/files/get/bucket'+filename,
            'org_filename':original_filename
        }, 200
    else:
        return{
            'message':'bad request'
        }, 400
    
