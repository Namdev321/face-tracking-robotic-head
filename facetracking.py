# By_SciCraft - Modified for ESP32

import cv2
from cvzone.FaceDetectionModule import FaceDetector
import numpy as np
import serial
import time

# ================= SERIAL =================
port = "COM9"   # change if different
esp = serial.Serial(port, 115200)
time.sleep(2)
# ==========================================

cap = cv2.VideoCapture(0)
ws, hs = 1280, 720
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera couldn't Access!!!")
    exit()

detector = FaceDetector()
servoPos = [90, 90]

while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img, draw=False)

    if bboxs:
    # get bbox info
        bbox = bboxs[0]
        x, y, w, h = bbox["bbox"]
        fx, fy = bbox["center"]
        
        # ===== DRAW BOX =====
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # center dot
        cv2.circle(img, (fx, fy), 10, (0, 0, 255), cv2.FILLED)

        # crosshair
        cv2.line(img, (0, fy), (ws, fy), (0, 0, 0), 2)
        cv2.line(img, (fx, 0), (fx, hs), (0, 0, 0), 2)

        # show coordinates
        cv2.putText(img, f"{fx},{fy}", (fx+15, fy-15),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    # ===== SERVO CALCULATION =====
        
        servoX = np.interp(fx, [0, ws], [180, 0])
        servoY = np.interp(fy, [0, hs], [180, 0])

        servoX = max(0, min(180, int(servoX)))
        servoY = max(0, min(180, int(servoY)))

        servoPos = [servoX, servoY]

        # send data → "90,120\n"
        data = f"{servoX},{servoY}\n"
        esp.write(data.encode())

        cv2.putText(img, "TARGET LOCKED", (850, 50),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    else:
        cv2.putText(img, "NO TARGET", (880, 50),
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    cv2.putText(img, f'Servo X: {servoPos[0]}', (50, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(img, f'Servo Y: {servoPos[1]}', (50, 100),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
