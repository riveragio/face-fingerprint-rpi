import face_recognition
import cv2
import numpy as np
import os
import time
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
import xlwt
from xlwt import Workbook
from datetime import date
import xlrd, xlwt
from xlutils.copy import copy as xl_copy
import serial
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

Buzzer = 7
GPIO.setup(Buzzer, GPIO.OUT)

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)


# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is not required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

CurrentFolder = os.getcwd() #Read current folder path
image = CurrentFolder+'/rahul.png'
image2 = CurrentFolder+'/Pranali.png'

# Load a sample picture and learn how to recognize it.
person1_name = "Rahul"
person1_image = face_recognition.load_image_file(image)
person1_face_encoding = face_recognition.face_encodings(person1_image)[0]

# Load a second sample picture and learn how to recognize it.
person2_name = "Pranali"
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

database = {
            0: [person1_name,"9763365197"],
            1: [person2_name,"8793418848"]
            }

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
attendance_taken_from_camera = 0

lcd.clear()
lcd.write_string('Smart Attendance')
lcd.crlf()
lcd.write_string(' System')
time.sleep(2)
lcd.clear()
lcd.write_string('Please Enter')
lcd.crlf()
lcd.write_string('Lecture Name')
time.sleep(2)
excel_file_name = 'attendance_excel.xls'
rb = xlrd.open_workbook(excel_file_name, formatting_info=True) 
wb = xl_copy(rb)
lecture_name = input('Please give current subject lecture name')
sheet1 = wb.add_sheet(lecture_name)
sheet1.write(0, 0, 'Name/Date')
sheet1.write(0, 1, str(date.today()))
row=1
col=0
already_attendence_taken = ""
lcd.clear()
lcd.write_string('Lecture Name')
lcd.crlf()
lcd.write_string(lecture_name)
time.sleep(2)


def message_send(number, student_name,lecture_name):
        gsm_ser=serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)
        gsm_ser.write("AT+CMGF=1\r\n".encode());    #Sets the GSM Module in Text Mode
        time.sleep(1);  # time.sleep of 1 milli seconds or 1 second
        gsm_ser.write(("AT+CMGS=\"+91"+number+"\"\r\n").encode()); # Replace x with mobile number
        time.sleep(1);
        gsm_ser.write(("Your Son/Daughter "+student_name+" attended today's "+lecture_name+" class"+"\r\n").encode());
        time.sleep(1);
        gsm_ser.write("\x1A".encode());# ASCII code of CTRL+Z
        time.sleep(1);
        print("Message Send")



while(1):
    ## Tries to initialize the sensor
    try:
        f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))

    try:
        #print('Waiting for finger...')
        lcd.clear()
        lcd.write_string('Please Scan')
        lcd.crlf()
        lcd.write_string('Your Finger')
        time.sleep(2)

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if ( positionNumber == -1 ):
            print('No match found!')
            lcd.clear()
            lcd.write_string('Student Database')
            lcd.crlf()
            lcd.write_string('Not Found')
            time.sleep(2)
        else:
            lcd.clear()
            lcd.write_string('Please Scan')
            lcd.crlf()
            lcd.write_string('Your Face')
            time.sleep(2)
            #print("attendence taken")
            #print('Found template at position #' + str(positionNumber))
            attendance_taken_from_camera = 0
            while(1):
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
                            if((already_attendence_taken != name) and (name != "Unknown") and (database[positionNumber][0] == name)):
                             already_attendence_taken = name
                             print("attendance taken")
                             attendance_taken_from_camera = 1
                             sheet1.write(row, col,database[positionNumber][0] )
                             col =col+1
                             sheet1.write(row, col, "Present" )
                             row = row+1
                             col = 0
                             wb.save(excel_file_name)
                             message_send(database[positionNumber][1],database[positionNumber][0],lecture_name)
                             lcd.clear()
                             lcd.write_string('Your Attendance')
                             lcd.crlf()
                             lcd.write_string('Taken '+database[positionNumber][0])
                             time.sleep(1)
                             GPIO.output(Buzzer, True)
                             time.sleep(1)
                             GPIO.output(Buzzer, False)
                             time.sleep(1)
                             lcd.clear()
                             lcd.write_string('Message send')
                             lcd.crlf()
                             lcd.write_string('to parent')
                             time.sleep(2)
                            elif(database[positionNumber][0] != name ):
                             lcd.clear()
                             lcd.write_string('Face and Finger')
                             lcd.crlf()
                             lcd.write_string('mismatched')
                             time.sleep(2)
                            elif((already_attendence_taken == name) ):
                             lcd.clear()
                             lcd.write_string('Attedance taken')
                             lcd.crlf()
                             lcd.write_string('Press Q Button ')
                             time.sleep(2)
                            else:
                             lcd.clear()
                             lcd.write_string('Student Database')
                             lcd.crlf()
                             lcd.write_string('Not Found')
                             time.sleep(2)
                                
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
                        cv2.destroyAllWindows()
                        break

            
        ## Loads the found template to charbuffer 1
        f.loadTemplate(positionNumber, 0x01)

    except Exception as e:
        print('Exception message: ' + str(e))

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
