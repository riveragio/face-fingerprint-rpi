import face_recognition
import cv2
import numpy as np
import os
import xlwt
from xlwt import Workbook
from datetime import date
import xlrd, xlwt
from xlutils.copy import copy as xl_copy
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 11
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 15
LCD_D7 = 16
Buzzer = 22

'''
define pin for lcd
'''
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
delay = 1

GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(Buzzer, GPIO.OUT) # DB7

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

'''
Function Name :lcd_init()
Function Description : this function is used to initialized lcd by sending the different commands
'''
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
'''
Function Name :lcd_byte(bits ,mode)
Fuction Name :the main purpose of this function to convert the byte data into bit and send to lcd port
'''
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
'''
Function Name : lcd_toggle_enable()
Function Description:basically this is used to toggle Enable pin
'''
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
'''
Function Name :lcd_string(message,line)
Function  Description :print the data on lcd 
'''
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)


CurrentFolder = os.getcwd() #Read current folder path
image = CurrentFolder+'/shubham.png'
image2 = CurrentFolder+'/sneha.png'


# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is not required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
person1_name = "Shubham"
person1_image = face_recognition.load_image_file(image)
person1_face_encoding = face_recognition.face_encodings(person1_image)[0]

# Load a second sample picture and learn how to recognize it.
person2_name = "sneha"
person2_image = face_recognition.load_image_file(image2)
person2_face_encoding = face_recognition.face_encodings(person2_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    person1_face_encoding,
    person2_face_encoding
]
known_face_names = [
    person1_name,
    person2_name
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

GPIO.output(Buzzer, False)
time.sleep(E_DELAY)
lcd_init()
lcd_byte(0x01,LCD_CMD) # 000001 Clear display
time.sleep(E_DELAY)
lcd_string("Smart Attendence ",LCD_LINE_1)
lcd_string(" System ",LCD_LINE_2)
time.sleep(2)

rb = xlrd.open_workbook('attendence_excel.xls', formatting_info=True) 
wb = xl_copy(rb)
lcd_byte(0x01,LCD_CMD) # 000001 Clear display
time.sleep(E_DELAY)
lcd_string("Please Enter ",LCD_LINE_1)
lcd_string("lecture Name",LCD_LINE_2)
time.sleep(E_DELAY)
inp = input('Please give current subject lecture name')
lcd_byte(0x01,LCD_CMD) # 000001 Clear display
time.sleep(E_DELAY)
lcd_string("Lecture Name ",LCD_LINE_1)
lcd_string(inp,LCD_LINE_2)
time.sleep(2)
sheet1 = wb.add_sheet(inp)
sheet1.write(0, 0, 'Name/Date')
sheet1.write(0, 1, str(date.today()))
row=1
col=0
already_attendence_taken = ""
lcd_byte(0x01,LCD_CMD) # 000001 Clear display
time.sleep(E_DELAY)
lcd_string("Please Scan",LCD_LINE_1)
lcd_string("Your Face",LCD_LINE_2)
time.sleep(E_DELAY)
while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)
                    if((already_attendence_taken != name) and (name != "Unknown")):
                     sheet1.write(row, col, name )
                     col =col+1
                     sheet1.write(row, col, "Present" )
                     row = row+1
                     col = 0
                     print("attendence taken")
                     wb.save('attendence_excel.xls')
                     already_attendence_taken = name
                     lcd_byte(0x01,LCD_CMD) # 000001 Clear display
                     time.sleep(E_DELAY)
                     lcd_string("Your Attendence",LCD_LINE_1)
                     lcd_string("Taken "+name,LCD_LINE_2)
                     time.sleep(2)
                     GPIO.output(Buzzer, True)
                     time.sleep(1)
                     GPIO.output(Buzzer, False)
                     time.sleep(1)
                    else:
                     print("next student")
                     lcd_byte(0x01,LCD_CMD) # 000001 Clear display
                     time.sleep(E_DELAY)
                     lcd_string("Please Scan Next",LCD_LINE_1)
                     lcd_string("Student Face",LCD_LINE_2)
                     time.sleep(E_DELAY)
                        
            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xff==ord('q'):   
                print("data save")
                break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
