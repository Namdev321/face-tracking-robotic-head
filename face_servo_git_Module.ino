#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  110   // adjust after testing
#define SERVOMAX  510

// channels
int servoX_ch = 0;
int servoY_ch = 1;

int angleToPulse(int ang) {
  return map(ang, 0, 180, SERVOMIN, SERVOMAX);
}

void setup() {
  Serial.begin(115200);
  pwm.begin();
  pwm.setPWMFreq(50);  // servo frequency
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');

    int comma = data.indexOf(',');
    if (comma > 0) {
      int x = data.substring(0, comma).toInt();
      int y = data.substring(comma + 1).toInt();

      pwm.setPWM(servoX_ch, 0, angleToPulse(x));
      pwm.setPWM(servoY_ch, 0, angleToPulse(y));
    }
  }
}
