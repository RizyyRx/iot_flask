from flask import Blueprint, redirect, url_for, request, render_template, session, Response, send_file
from src.User import User
from src.Database import Database
from gridfs import GridFS, GridFSBucket
import mimetypes
import uuid

bp = Blueprint("files",__name__,url_prefix="/files")

@bp.route("/upload/bucket",methods=['POST'])
def upload_bucket():
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
    
# modern way to get files from db (Not recommended when dealing with big files)
@bp.route("/get/bucket/<filename>",methods=['GET'])
def get_bucket(filename):
    if session['authenticated']:
        try:
            fs = GridFSBucket(Database.get_connection())

            #using gridfs bucket with this for larger files like gr than 16mb is not recommended
            #since it has to load the whole file to the RAM and it may crash the server
            file = fs.open_download_stream_by_name(filename)
            # using Response, we can send our crafted response to the browser
            # we have to explicitly mention the content type to the response so that browser can understand the filetype and display it appropriately
            # the filetype is stored in HTML header
            response = Response(file.read(),status = 200,mimetype=file.metadata['content_type'])
            return response
        except:
            return{
                'message':"file not found"
            }, 404
    else:
        return{
            'message':'bad request'
        }, 400

# A bit low level way to put files (not recommended when dealing with big files)
@bp.route("/put",methods=['POST'])
def put_fs():
    if(session['authenticated']):
        fs = GridFS(Database.get_connection())
        file = request.files['file']
        filename = str(uuid.uuid4())
        metadata = {
            'original_filename':file.filename,
            'content_type':mimetypes.guess_type(file.filename)[0],
            'owner':session.get('username')
        }
        file_id = fs.put(file,filename=filename,metadata=metadata)
        return{
            'message':"upload_success",
            'filename':filename,
            'file_id':str(file_id),
            'download_url':'/files/get/'+filename,
            'org_filename':file.filename
        }, 200
    else:
        return{
            'message':'bad request'
        }, 400

# A bit low level way to get files (still not recommended when dealing with big files)
@bp.route("/get/<filename>",methods=['GET'])
def get_fs(filename):
    if(session['authenticated']):
        fs = GridFS(Database.get_connection())
        file = fs.find_one({
            'filename':filename
        })
        if file is None:
            return{
                'message':"file not found"
            }, 404
        return send_file(file,mimetype=file.metadata['content_type'])
        # use below return to make the file instantly downloadable
        # return send_file(file,mimetype=file.metadata['content_type'],as_attachment=True, download_name=file.metadata['original_filename'])
    else:
        return{
            'message':'bad request'
        }, 400

#TODO: add delete functionality, only del when current user == uploaded user

@bp.route("/stream/<filename>",methods=['GET'])
def stream_fs(filename):
    db = Database.get_connection()
    file_doc = db.fs.files.find_one({  #query for file name inside fs.files in db using filename
        'filename':filename
    })

    if file_doc is None:
        return{
                'message':"file not found"
            }, 404
    
    # all of these parameters are present in the find_one() inside db
    total_size = file_doc['length']
    chunk_size = file_doc['chunkSize']
    mimetype = file_doc['metadata']['content_type']

    # The Range header is checked in the incoming HTTP request, allowing clients to request specific byte ranges
    range_header = request.headers.get('Range',None)
    if not range_header:
        start_byte = 0
        end_byte = chunk_size - 1 # -1 to compensate since we're starting with 0
    else:
        range_bytes = range_header.split("=")[1] # if range_header has "bytes=0-1023", using range_header.split("="), we get ['bytes', '0-1024'], so we take index 1, only the bytes range (i.e "0-1023")
        range_split = range_bytes.split("-") # we get ['0', '1023'] here
        # take the 0 and 1 index as start and end bytes value
        # Handle cases where start or end byte is missing
        start_byte = int(range_split[0]) if range_split[0] else 0  # Default to 0 if missing
        end_byte = int(range_split[1]) if range_split[1] else total_size - 1  # Default to end of file if missing

        

    # start_chunk and end_chunk are calculated to find which chunks (stored by chunk_size) contain the requested byte range.
    start_chunk = start_byte // chunk_size # Ex: If total bytes are 100000 for a file, requested byte range is 60000 - 80000, and one chunk size is 20000, we can calc in which chunk does the req bytes start by doing 60000 // 20000, we get 3.
    end_chunk = end_byte // chunk_size # same for end_chunk, here we use end_byte to calc


    def stream():
        for chunk_number in range(start_chunk, end_chunk + 1): # +1 to compensate because ranges in python are exclusive for end value in range()
            chunk = db.fs.chunks.find_one({ # get the chunk data one by one using file_id and chunk number
                'files_id': file_doc['_id'],
                'n': chunk_number
            })
            '''
            > start_index will calc from where to start our yield of bytes for each chunks according to the requested range
            > Take example of request of 4500000 - 6500000
            > (chunk_number * chunk_size) represents what is the current total bytes from 0 according to chunk_number
            > If chunk_number is 4 and chunk_size is 1000000(1mb), we get 4000000(4mb)
            > If start_byte is 450000, now doing start_byte - (above calc), we get max(0,500000)
            > max(0,500000) is 500000, we got exact byte value of where to start
            > If chunk_number is 5, (chunk_number * chunk_size) is 5000000
            > start_byte - (chunk_number * chunk_size) is 4500000 - 5000000, we get -500000
            > max(0,-500000) is 0, so using this whole logic, we can get start_index without any problem
            > in-between values of bytes according to requests can be retrived using this calc
            '''
            start_index = max(0,start_byte - (chunk_number * chunk_size))

            '''
            > end_index will calc when we have to end yield for each chunks according to requested range
            > According to our example, if chunk_number is 5 in iteration, end_byte - (chunk_number * chunk_size) is 6500000 - (5000000)
            > we get 1500000, and min(1000000,1500000) will give 1000000. It handles "if val goes above the default chunk size" condition
            > At chunk_number 6, end_byte - (chunk_number * chunk_size) is 6500000 - (6000000), we get 500000
            > min(1000000, 500000) is 500000, so we get exactly the last 500000 instead of whole chunk_size as per requested range
            '''
            end_index = min(chunk_size, end_byte - (chunk_number * chunk_size))

            # yield allows data to be sent in small chunks, freeing memory after each part is sent, enabling efficient streaming without loading the entire dataset into memory at once.
            yield chunk['data'][start_index:end_index]
    
    # Create a response object that streams data in chunks by calling the stream() generator,
    # setting the HTTP status to 206 (Partial Content) to indicate that only a portion of the file is being sent, and specifying the MIME type for the file format.
    response = Response(stream(), status=206, mimetype=mimetype, direct_passthrough=True)

    # Add the Content-Range header to indicate the byte range of the data being sent
    # (start-end/total_size), which helps the client know which part of the file is being streamed.
    response.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start_byte, end_byte, total_size))

    # Add the Accept-Ranges header to indicate that the server supports partial content requests,
    # allowing clients to request specific byte ranges for efficient data retrieval.
    response.headers.add('Accept-Ranges', 'bytes')

    # Return the response object, which streams the requested byte range to the client.
    return response

# The Response object manages the timing of each yield call based on client readiness.
# It requests each new chunk from the generator (stream()) only after the client signals it’s ready for more data.
# This flow-controlled, chunk-by-chunk approach keeps memory usage low while adapting to the client’s speed of data consumption.
