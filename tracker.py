import cv2
import mediapipe as mp
from cvzone.FaceDetectionModule import FaceDetector
import time
import serial
import numpy as np


port = "COM9"
esp = serial.Serial(port, 115200)
time.sleep(2)


cap = cv2.VideoCapture(0)
ws, hs = 1280, 720     #sets the resolution
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera coudn_t Access!")
    exit()

return_delay = 5
scan_delay = 30

detector = FaceDetector()
last_face_time = time.time()

servoX = 90
servoY = 90
centerX_angle = 90
centerY_angle = 90

#========== Sacn Setting ============
scan_direction = 1
scan_speed = 2
scan_min = 30
scan_max = 150
#vertical check
vertical_position = [90, 60, 120]
vertical_index = 0
checking_vertical = False

# ====== DEAD Zone Setting=========
dead_zone = 40          # pixels
speed = 3               # smooth movement speed

while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img, draw = False)
    current_time = time.time()

    if bboxs:
        last_face_time = current_time
        bbox = bboxs[0]
        x, y, w, h = bbox["bbox"] # it return the dimensions of image from the module dictionary
        fx, fy = bbox["center"]   # it return the center dime

            # ( img, pt1,pt2,color,scalar)
        cv2.rectangle(img,(x, y),(x + w, y + h), (0, 255, 0 ), 2)

        gap = max(20, int(w * 0.5))
        cv2.line(img,(0,fy),(fx-gap,fy),(0, 255, 0),2)
        cv2.line(img,(fx + gap, fy), (ws, fy), (0, 255, 0),2)
        
        cv2.line(img,(fx,0),(fx,fy-gap),(0, 255, 0),2)
        cv2.line(img,(fx,fy+gap),(fx,hs),(0, 255, 0),2)

        cv2.putText(img,"TARGET LOCKED", 
                    (950,50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255,255,0),3)
        # ======== Servo Calculation = ===============

        targetX = np.interp(fx, [0, ws], [180, 0])  # it update servo X position
        targetY = np.interp(fy, [0, hs], [180, 0])  # it update servo Y position

        #=========== DEAD ZONE =================
        if abs(fx - ws//2) < dead_zone:
            targetX = servoX
        if abs ( fy - hs//2) < dead_zone:
            targetY = servoY

        # SmOOOTH MOVEMENT
        # horixontal
        if servoX < targetX: #right
            servoX += min(speed, targetX - servoX)
        elif servoX > targetX: #left
            servoX -= min(speed, servoX - targetX)
        # vertical
        if servoY < targetY: # up
            servoY += min(speed, targetY - servoY)
        if servoY > targetY: # down
            servoY -= min(speed, servoY - targetY)



    else:
        time_since_seen = current_time - last_face_time  # this logic count the time in sec
        # print(int(time_since_seen))

        if time_since_seen < return_delay:
            remaining = int(return_delay - time_since_seen)
            cv2.putText(img, f"NO TARGET - RETURNING CENTER IN {remaining}s",
                        (600,50),
                        cv2.FONT_HERSHEY_PLAIN,2, (0, 0, 255), 3)
        else: 
            remaining = int(scan_delay - time_since_seen)

            # === Horizontal check =+=======
            if not checking_vertical:
                servoX += scan_direction * scan_speed
                # Add Center Check Here
                if abs(servoX - 90) < 2 and not checking_vertical: # right
                    checking_vertical = True
                    vertical_index = 0
                if servoX >= scan_max: 
                    servoX = scan_max
                    scan_direction = -1
                    checking_vertical = True
                    vertical_index = 0
                
                elif servoX <= scan_min:
                    servoX = scan_min
                    scan_direction = 1
                    checking_vertical = True
                    vertical_index = 0
            else:
                targetY = vertical_position[vertical_index]
                if abs(servoY - targetY) > 2:
                    if servoY < targetY:
                        servoY += 2
                    else:
                        servoY -= 2
                else:
                    vertical_index += 1
                    if vertical_index >= len(vertical_position):
                        checking_vertical = False





            cv2.putText(img,f"SCANNING...",
                        (900, 50),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 3)
            if time_since_seen > scan_delay:
                    # Move back to center smoothly
                if servoX < 90:
                    servoX += 2
                elif servoX > 90:
                    servoX -= 2

                if servoY < 90:
                    servoY += 2
                elif servoY > 90:
                    servoY -= 2

    # ===== LIMIT RANGE =====
    # max(0, result)
    servoX = int(max(0, min(180, servoX)))
    servoY = int(max(0, min(180, servoY)))

    # ===== SEND TO ESP32 =====
    data = f"{servoX},{servoY}\n"
    esp.write(data.encode())

    cv2.putText(img, f'Servo X :{servoX}',(50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
    cv2.putText(img, f'Servo X :{servoY}',(50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)

    cv2.imshow("This is A Smart Atuo Track Robot",img)
    if cv2.waitKey(1) & 0xff == ord("p"):
        break

# cap.release()
# cv2.destroyAllWindows()