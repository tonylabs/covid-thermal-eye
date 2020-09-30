#!/usr/bin/env python

#https://github.com/galaunay/pypyueye

import os
import cv2
import numpy as np
import face_recognition
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

    ###
    path = 'images/photos'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('attendance.csv', 'r+') as f:
            myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
        nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        f.writelines(f'\n{name},{dtString}')

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
    # img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
    print(faceDis)
    matchIndex = np.argmin(faceDis)

    if matches[matchIndex]:
        name = classNames[matchIndex].upper()
    print(name)
    y1, x2, y2, x1 = faceLoc
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
    markAttendance(name)
    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

    ###
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
        cv2.imshow("Thermal Eye", gray)
        # press 'q' to remove window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    objCamera.release()
    cv2.destroyAllWindows()

    cv2.waitKey(0)
    '''