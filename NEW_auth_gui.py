import os
import cv2
import face_recognition
import time
import tkinter as tk
import subprocess
from pyfingerprint.pyfingerprint import PyFingerprint
from PIL import Image, ImageTk

cap = cv2.VideoCapture(0)

# Function to open a camera frame
def update_camera():
    ret, frame = cap.read()
    if ret:
        # Convert the frame to ImageTk format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.config(image=imgtk)
    window.after(10, update_camera)  # refresh every 10ms

# Load known face encodings
def load_known_faces(folder_path='faces'):
    known_encodings = []
    known_names = []
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        img = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

# Fingerprint authentication
def authenticate_fingerprint():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if not f.verifyPassword():
            return None
    except Exception as e:
        return None

    status_label.config(text="Waiting for fingerprint...")
    window.update()

    while not f.readImage():
        pass

    f.convertImage(0x01)
    result = f.searchTemplate()
    position_number = result[0]

    if position_number >= 0:
        return position_number
    return None

# Face recognition
def authenticate_face(known_encodings, known_names):
    #cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return None

    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    for encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        if True in matches:
            idx = matches.index(True)
            return known_names[idx]
    return None

# Authentication logic
def start_auth():
    status_label.config(text="Starting Face Recognition...\n\nLook at the Camera")
    window.update()

    known_encodings, known_names = load_known_faces()
    face_name = authenticate_face(known_encodings, known_names)

    if not face_name:
        status_label.config(text="Face not recognized")
        return

    status_label.config(text="Face Recognized!!!\n\nPlace your finger on the sensor...")
    window.update()
    time.sleep(3)

    finger_id = authenticate_fingerprint()
    if finger_id is None:
        status_label.config(text="Fingerprint failed")
        return

    status_label.config(text=f"Access Granted!\nWelcome {face_name}")

def on_closing():
    cap.release()
    window.destroy()

# GUI setup
window = tk.Tk()
window.title("Dual Authentication (SNA1 LAB 206)")
window.geometry("850x750")
window.resizable(False, False)

tk.Label(window, text="Dual Authentication System\n(Face and Fingerprint Recognition)\n\nby Geri's Networking Company", font=("Helvetica", 16)).pack(pady=20)
tk.Button(window, text="Start Authentication", command=start_auth, font=("Helvetica", 12)).pack(pady=10)
status_label = tk.Label(window, text="", font=("Helvetica", 12), fg="blue")
status_label.pack(pady=20)
# Camera preview at bottom
camera_label = tk.Label(window)
camera_label.pack(pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)
update_camera()
window.mainloop()
