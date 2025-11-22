import os
import cv2
import face_recognition
import pickle

ENCODINGS_FILE = "face_encodings.pkl"
FACES_DIR = "registered_faces"

def ensure_dirs():
    if not os.path.exists(FACES_DIR):
        os.makedirs(FACES_DIR)

def load_encodings():
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_encodings(encodings):
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(encodings, f)

def register_face(image, roll_no):
    ensure_dirs()
    encodings = load_encodings()
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) != 1:
        return False, "Please ensure only one face is visible for registration."
    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
    encodings[roll_no] = face_encoding
    save_encodings(encodings)
    # Save the image for reference
    cv2.imwrite(os.path.join(FACES_DIR, f"{roll_no}.jpg"), image)
    return True, "Face registered successfully."

def recognize_face(image):
    encodings = load_encodings()
    if not encodings:
        return None
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None
    face_encodings = face_recognition.face_encodings(image, face_locations)
    for face_encoding in face_encodings:
        for roll_no, known_encoding in encodings.items():
            match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)
            if match[0]:
                return roll_no
    return None 

def deregister_face(roll_no):
    # Remove encoding
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            encodings = pickle.load(f)
        if roll_no in encodings:
            del encodings[roll_no]
            with open(ENCODINGS_FILE, "wb") as f:
                pickle.dump(encodings, f)
            print(f"Removed encoding for {roll_no}")
        else:
            print(f"No encoding found for {roll_no}")
    # Remove image
    img_path = os.path.join(FACES_DIR, f"{roll_no}.jpg")
    if os.path.exists(img_path):
        os.remove(img_path)
        print(f"Removed image for {roll_no}")
    else:
        print(f"No image found for {roll_no}")