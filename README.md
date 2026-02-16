# face-tracking-robotic-head
AI-powered robotic head that detects and tracks human faces in real time using OpenCV. A Python vision system sends coordinates to an ESP32, which drives servos via PCA9685 for pan–tilt motion. Demonstrates computer vision, embedded control, and hardware–software integration.

Connections 
🧩 ESP32 ↔ PCA9685 (I2C)

PCA9685	              ESP32
--------------------------------
VCC	                  3.3V
GND	                  GND
SDA	                  GPIO 21
SCL                  	GPIO 22



🧩 Servo Power (VERY IMPORTANT ⚠) :
                                      External 5–6V → PCA9685 V+
                                      External GND → PCA9685 GND


            
<img width="1231" height="662" alt="image" src="https://github.com/user-attachments/assets/0f237ee8-2207-4fa9-828b-3cf6989b46e4" />

