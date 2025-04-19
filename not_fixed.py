import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import os
from pyfingerprint.pyfingerprint import PyFingerprint
import time
import threading

# ---------- Load known faces ----------
known_face_encodings = []
known_face_names = []

for filename in os.listdir('known_faces'):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join('known_faces', filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(os.path.splitext(filename)[0])
        else:
            print(f"Warning: No face found in {filename}")

# ---------- Fingerprint Authentication ----------
def fingerprint_authenticate():
    print("[Fingerprint] Waiting for finger...")

    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('Wrong fingerprint sensor password!')

    except Exception as e:
        print(f'Fingerprint init failed: {str(e)}')
        return False

    while not f.readImage():
        pass

    f.convertImage(0x01)

    result = f.searchTemplate()
    positionNumber = result[0]

    if positionNumber >= 0:
        print(f"Fingerprint recognized at position #{positionNumber}")
        return True
    else:
        print("Fingerprint not recognized.")
        return False

# ---------- Facial Recognition ----------
def face_authenticate():
    print("[Face] Scanning...")
    cam = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if not cam.isOpened():
        print("Camera error.")
        return None

    time.sleep(2)  # Allow time for camera to initialize

    # Reduce camera resolution to reduce memory usage
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Use a lower resolution for Raspberry Pi
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        ret, frame = cam.read()
        if not ret:
            print(""Error reading frame from camera.")
            cam.release()
            return None

        rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Draw rectangle around the face (for visualization)
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Show the frame with the face
        cv2.imshow("Face Authentication - Press 'q' to quit", frame)

        # Check if face is recognized
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            if True in matches:
                matched_index = matches.index(True)
                name = known_face_names[matched_index]
                print(f"Face recognized: {name}")
                cam.release()
                cv2.destroyAllWindows()
                return name

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print("Face not recognized.")
    return None

# ---------- GUI Main Window ----------
def on_authenticate_button_click():
    # Reset status
    status_label.config(text="Authenticating...")

    # Start dual authentication process in a separate thread to avoid blocking UI
    auth_thread = threading.Thread(target=dual_authentication)
    auth_thread.start()

def dual_authentication():
    # Start the fingerprint authentication process first
    if not fingerprint_authenticate():
        status_label.config(text="Access Denied: Fingerprint mismatch.")
        return

    # Proceed with facial recognition if fingerprint is successful
    user = face_authenticate()
    if not user:
        status_label.config(text="Access Denied: Face not recognized.")
        return

    status_label.config(text=f"Access granted to {user}!")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Dual Authentication System")

# Window Size
root.geometry("400x300")

# Title Label
title_label = tk.Label(root, text="Dual Authentication", font=("Arial", 16))
title_label.pack(pady=20)

# Authentication Button
authenticate_button = tk.Button(root, text="Start Authentication", command=on_authenticate_button_click, font=("Arial", 14))
authenticate_button.pack(pady=20)

# Status Label
status_label = tk.Label(root, text="Please click to authenticate", font=("Arial", 12))
status_label.pack(pady=20)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12))
exit_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()

