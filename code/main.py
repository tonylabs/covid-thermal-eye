#!/usr/bin/env python

#https://github.com/galaunay/pypyueye

import os
import cv2
import numpy as np
import face_recognition
import db as orm
from datetime import datetime
import conf.db as db
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

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

    ###Get Photo Files
    path = 'images/photos'
    images = []
    filenames = []
    files = os.listdir(path)
    #print(files)
    for file in files:
        curImg = cv2.imread(f'{path}/{file}')
        images.append(curImg)
        filenames.append(os.path.splitext(file)[0])
    #print(filenames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        print(name)

    encodeListKnown = findEncodings(images)

    objCamera = cv2.VideoCapture(0)
    while True:
        success, img = objCamera.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = filenames[matchIndex].upper()
                print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)
        cv2.imshow('TONYLABS THERMAL EYE', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    '''
    try:
        conn = mysql.connector.connect(user=db.mysql["user"], password=db.mysql["password"], host=db.mysql["host"], database=db.mysql["db"])
        sql = """INSERT INTO `tlabs_user_temperature` (`user_id`, `temperature`) VALUES (1, 35.36)"""
        cursor = conn.cursor()
        result = cursor.execute(sql)
        conn.commit()
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (conn.is_connected()):
            conn.close()
            print("MySQL connection is closed")
    '''