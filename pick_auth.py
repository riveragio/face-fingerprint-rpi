import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Path to your other scripts
FACE_SCRIPT = "face_module.py"
FINGERPRINT_SCRIPT = "fingerprint_module.py"

def run_script(script_name):
    if os.path.exists(script_name):
        subprocess.Popen(["python", script_name])
    else:
        messagebox.showerror("File Not Found", f"{script_name} not found!")

# GUI setup
root = tk.Tk()
root.title("Biometric System")
root.geometry("400x250")
root.configure(bg="#f0f0f0")

title = tk.Label(root, text="Select Biometric Method", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
title.pack(pady=30)

# Face Recognition Button
face_button = tk.Button(root, text="Face Recognition", width=20, height=2, font=("Helvetica", 12),
                        bg="#4CAF50", fg="white", command=lambda: run_script(FACE_SCRIPT))
face_button.pack(pady=10)

# Fingerprint Recognition Button
finger_button = tk.Button(root, text="Fingerprint Recognition", width=20, height=2, font=("Helvetica", 12),
                          bg="#2196F3", fg="white", command=lambda: run_script(FINGERPRINT_SCRIPT))
finger_button.pack(pady=10)

root.mainloop()
