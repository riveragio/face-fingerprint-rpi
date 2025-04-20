import os
import cv2
import face_recognition
from pyfingerprint.pyfingerprint import PyFingerprint
import time

# Load known faces
def load_known_faces(folder_path='faces'):
    known_encodings = []
    known_names = []

    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        img = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(filename)[0])

    return known_encodings, known_names

# Authenticate via fingerprint
def authenticate_fingerprint():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('Fingerprint sensor password is incorrect.')

    except Exception as e:
        print(f'Fingerprint initialization failed: {e}')
        return None

    print('Place finger on sensor...')
    while f.readImage() == False:
        pass

    f.convertImage(0x01)
    result = f.searchTemplate()
    position_number = result[0]

    if position_number >= 0:
        print(f'Fingerprint recognized at position #{position_number}')
        return position_number
    else:
        print('No match found for fingerprint.')
        return None

# Authenticate via face
def authenticate_face(known_encodings, known_names):
    print("Initializing camera...")
    cap = cv2.VideoCapture(0)
    time.sleep(2)

    print("Look at the camera...")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return None

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        print("No face detected.")
        return None

    # Compute encodings only if a face is detected
    encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        if True in matches:
            matched_idx = matches.index(True)
            name = known_names[matched_idx]
            print(f"Face recognized: {name}")
            return name

    print("Face not recognized.")
    return None


# Main dual-authentication
def main():
    print("=== DUAL AUTHENTICATION START ===")

    # Step 1: Fingerprint auth
    finger_id = authenticate_fingerprint()
    if finger_id is None:
        print("Authentication failed at fingerprint stage.")
        return

    # Step 2: Face recognition
    known_encodings, known_names = load_known_faces()
    face_name = authenticate_face(known_encodings, known_names)

    if face_name is not None:
        print(f"ACCESS GRANTED: {face_name}")
    else:
        print("Authentication failed at facial recognition stage.")

if __name__ == "__main__":
    main()
