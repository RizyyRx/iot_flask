from mongogettersetter import MongoGetterSetter
from src.Database import Database
from time import time
from uuid import uuid4
from src import md5_hash
from src import get_config
import requests
import mimetypes
import face_recognition
import os
from PIL import Image
import numpy as np
from io import BytesIO

# Global variable to track the last successful match time and result
last_success_time = 0

# Global variable to store the last alert timestamp
last_alert_time = 0  # Initially set to 0

db = Database.get_connection()

class APICollection(metaclass=MongoGetterSetter):
    def __init__(self,id):
        self._collection = db.api_keys
        self._filter_query = {'$or': [
            {'id': id},
            {'hash': id}
        ]}

# when API object is created in register_api_key, it inherits the behavior defined by the metaclass MongoGetterSetter.
class API:
    def __init__(self,id):
        self.collection = APICollection(id) # self.collection will have the getter/setter functionality defined in MongoGetterSetter
        try:
            self.id = str(self.collection.id)
        except TypeError:
            raise Exception("API Key not found")
            
    def get_device(self):
        device = db.devices.find_one({"api": self.collection.hash})
        return device

    def is_valid(self):
        login_time = self.collection.time
        validity = self.collection.validity
        if validity == 0:
            return self.collection.active # if validity is 0, just return if active is true or false
        else:
            if self.collection.active: #if validity is not 0 and active is true, check validity status
                now = time()
                return now - login_time < validity
            else: #if validity is not 0 and active is false, return false
                return False 

    def delete(self):
        self.collection.delete()
        
    #get all api keys registered by username 
    @staticmethod
    def get_all_keys(session, only_unlinked=False): #only_unlinked is false by default, if set to true explicitly, it will filter api keys with only unlinked api keys
        if not session.get('authenticated') or not session.get('username'):
            raise Exception("not authenticated")
        
        username = session.get("username")
        collection = db.api_keys
        if only_unlinked:
            query = {"username": username, "linked_device": None}
        else:
            query = {"username": username}
        result = collection.find(query)
        return result

    @staticmethod
    def get_keys_count(session):
        if session.get('authenticated') or session.get('username'):
            username = session.get("username")
            collection = db.api_keys
            result = collection.count_documents({"username":username})
            return result

    @staticmethod
    def get_images_count(session):
        if session.get('authenticated') or session.get('username'):
            username = session.get("username")
            collection = db.motion_capture
            result = collection.count_documents({"owner":username})
            return result

    # registers api key entry in session collection on db with _type='api'
    @staticmethod
    def register_api_key(session, name, group, remarks, request=None, validity=0, _type="api"):
        if not session.get('authenticated') or not session.get('username'):
            raise Exception("User not authenticated")
        uuid = str(uuid4())
        collection = db.api_keys
        username = session.get('username')

        if request is not None:
            request_info = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'data': request.get_data().decode('utf-8')
            }
        else:
            request_info = None

        result = collection.insert_one({
            "id":uuid,
            "hash": md5_hash(uuid),
            "username":username,
            "name":name,
            "group":group,
            "remarks":remarks,
            "time":time(),
            "validity":validity,
            "active":True,
            "type":_type,
            "request":request_info,
            "linked_device": None
        })

        return API(uuid) # This uuid is the api key

    def send_telegram_alert():
        global last_alert_time  # Allow modification of the global variable
        
        current_time = time()  # Get current timestamp
        cooldown = 10  # 5 minutes in seconds

        # Check if 5 minutes have passed since the last alert
        if current_time - last_alert_time < cooldown:
            print("[INFO] Alert suppressed: 5-minute cooldown is active.")
            return  # Exit function without sending an alert

        try:
            bot_token = get_config("bot_token")
            chat_id = get_config("chat_id")
            message = "🚨 Motion detected! Check your camera now on the website."
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {"chat_id": chat_id, "text": message}

            response = requests.post(url, data=data, timeout=10)  # 10 sec network timeout
            response.raise_for_status()  # Raises an error for HTTP errors

            last_alert_time = current_time  # Update last alert time after successful send

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send Telegram alert: {e}")

    def compare_faces(file_id, fs):
        """ Extract image from GridFS and compare it with a reference face.
            If a positive match is found, prevent running again for 1 minute.
        """
        global last_success_time
        cooldown_period = 10  # timeout in seconds

        # Check if the function was called recently after a successful match
        if time() - last_success_time < cooldown_period:
            return None, None  # Do nothing during timeout

        # Reference Image Path
        reference_image_path = r"D:\flask\reference.jpg"
        
        try:
            # Fetch the image from GridFS
            file_data = fs.open_download_stream(file_id)
            image_bytes = file_data.read()
            file_data.close()

            # Convert image bytes to numpy array
            try:
                image = Image.open(BytesIO(image_bytes)).convert("RGB")  # Ensure RGB mode
            except UnidentifiedImageError:
                return "Invalid or Unsupported Image Format", None
            
            image = np.array(image)

            # Load the reference image
            reference_image = face_recognition.load_image_file(reference_image_path)
            reference_encodings = face_recognition.face_encodings(reference_image)

            if not reference_encodings:
                return "No face detected in reference image", None

            reference_encoding = reference_encodings[0]  # Use the first detected face

            # Get encodings from the uploaded image
            captured_encodings = face_recognition.face_encodings(image)

            if not captured_encodings:
                return "No face detected in uploaded image", None

            # Compare with multiple detected faces
            matched_faces = []

            for captured_encoding in captured_encodings:
                match = face_recognition.compare_faces([reference_encoding], captured_encoding)
                distance = face_recognition.face_distance([reference_encoding], captured_encoding)[0]
                similarity_score = 1 - min(distance, 1.0)  # Ensure it stays within 0-1 range

                if match[0]:
                    matched_faces.append(similarity_score)

            if matched_faces:
                best_match = max(matched_faces)  # Get the highest similarity score
                last_success_time = time()  # Update timestamp

                #send telegram alert for face match found
                try:
                    bot_token = get_config("bot_token")
                    chat_id = get_config("chat_id")
                    message = "similar face detected"
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    data = {"chat_id": chat_id, "text": message}

                    response = requests.post(url, data=data, timeout=10)  # 10 sec network timeout
                    response.raise_for_status()  # Raises an error for HTTP errors

                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Failed to send Telegram alert: {e}")
                return "Matched", round(best_match, 2)  # Return only when a match is found

            return "No Match", 0.0

        except Exception as e:
            return f"Error: {str(e)}", None