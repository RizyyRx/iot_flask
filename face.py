import face_recognition
import os

# Load and encode the reference image
reference_image_path = "reference.jpg"
captured_image_path = "cap3.png"  # Latest captured image

if not os.path.exists(reference_image_path):
    print("Reference image not found.")
    exit()

reference_image = face_recognition.load_image_file(reference_image_path)
reference_encodings = face_recognition.face_encodings(reference_image)

if not reference_encodings:
    print("No face detected in the reference image.")
    exit()

reference_encoding = reference_encodings[0]  # Use the first detected face

# Load and process the captured image
if os.path.exists(captured_image_path):
    captured_image = face_recognition.load_image_file(captured_image_path)
    captured_encodings = face_recognition.face_encodings(captured_image)

    if captured_encodings:
        print(f"Detected {len(captured_encodings)} faces in the captured image.")
        matched_faces = []

        for i, captured_encoding in enumerate(captured_encodings):
            match = face_recognition.compare_faces([reference_encoding], captured_encoding)
            distance = face_recognition.face_distance([reference_encoding], captured_encoding)[0]
            similarity_score = 1 - min(distance, 1.0)  # Ensure it stays within 0-1 range

            if match[0]:
                matched_faces.append((i + 1, similarity_score))  # Store (face_index, score)

        if matched_faces:
            best_match = max(matched_faces, key=lambda x: x[1])  # Find the highest similarity score
            print(f"Best Match: Face #{best_match[0]} with Similarity Score: {best_match[1]:.2f}")
        else:
            print("No Match Found.")
    else:
        print("No face detected in the captured image.")
else:
    print("Captured image not found.")

