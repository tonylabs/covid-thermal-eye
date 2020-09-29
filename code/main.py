#!/usr/bin/env python
import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import conf.db as db
import mysql.connector
from mysql.connector import Error

def list_ports():
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return available_ports,working_ports

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #list_ports()

    ###
    try:
        objConn = mysql.connector.connect(user=db.mysql["user"], password=db.mysql["password"], host=db.mysql["host"], database=db.mysql["db"])
        cursor = objConn.cursor()
        stringSQL = """SELECT * FROM `users` LIMIT 0,1"""
        print("MySQL connection is connected")
    except mysql.connector.Error as error:
        print("MySQL connectivity error: {}".format(error))
    finally:
        if (objConn.is_connected()):
            cursor.close()
            objConn.close()
            print("MySQL connection is closed")



    imgElon = face_recognition.load_image_file('images/elon-musk.jpg')
    imgElon = cv2.cvtColor(imgElon, cv2.COLOR_BGR2RGB)
    imgTest = face_recognition.load_image_file('images/bill-gates.jpg')
    imgTest = cv2.cvtColor(imgTest, cv2.COLOR_BGR2RGB)

    faceLoc = face_recognition.face_locations(imgElon)[0]
    encodeElon = face_recognition.face_encodings(imgElon)[0]
    cv2.rectangle(imgElon, (faceLoc[3], faceLoc[0]), (faceLoc[1], faceLoc[2]), (255, 0, 255), 2)

    faceLocTest = face_recognition.face_locations(imgTest)[0]
    encodeTest = face_recognition.face_encodings(imgTest)[0]
    cv2.rectangle(imgTest, (faceLocTest[3], faceLocTest[0]), (faceLocTest[1], faceLocTest[2]), (255, 0, 255), 2)

    results = face_recognition.compare_faces([encodeElon], encodeTest)
    faceDis = face_recognition.face_distance([encodeElon], encodeTest)
    print(results, faceDis)
    cv2.putText(imgTest, f'{results} {round(faceDis[0], 2)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Elon Musk', imgElon)
    cv2.imshow('Elon Test', imgTest)

    objCamera = cv2.VideoCapture(0)
    while (True):

        # capture frame-by-frame
        ret, frame = objCamera.read()
        # Gray scale conversion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # display the resulting frame
        cv2.imshow("goeduhub", gray)
        # press 'q' to remove window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    objCamera.release()
    cv2.destroyAllWindows()

    cv2.waitKey(0)