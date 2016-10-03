#include <QTRSensors.h>
#include <ZumoReflectanceSensorArray.h>
#include <ZumoMotors.h>
#include <ZumoBuzzer.h>
#include <Pushbutton.h>

ZumoReflectanceSensorArray reflectanceSensors;
ZumoBuzzer buzzer;
ZumoMotors motors;
Pushbutton button(ZUMO_BUTTON);
int lastError = 0;
const int MAX_SPEED = 400;

void setup() {
  buzzer.play(">g32>>c32");
  reflectanceSensors.init();
  button.waitForButton();
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
  delay(1000);
  int i;
  for(i = 0; i < 80; i++){
    if ((i > 10 && i <= 30) || (i > 50 && i <= 70))
      motors.setSpeeds(-200, 200);
    else
      motors.setSpeeds(200, -200);
    reflectanceSensors.calibrate();
    delay(20);
    }
  motors.setSpeeds(0,0);
  digitalWrite(13, LOW);
  buzzer.play(">g32>>c32");
  button.waitForButton();
  buzzer.play("L16 cdegreg4");
}

void loop() {
  unsigned int sensors[6];
  int position = reflectanceSensors.readLine(sensors);
  //error interval default = 2500
  int error = position - 2000;
  int speedDifference = error / 4 + 6 * (error - lastError);
  lastError = error;
  int m1Speed = MAX_SPEED + speedDifference;
  int m2Speed = MAX_SPEED - speedDifference;
  if (m1Speed < 0)    m1Speed = 0;
  if (m2Speed < 0)    m2Speed = 0;
  if (m1Speed > MAX_SPEED)    m1Speed = MAX_SPEED;
  if (m2Speed > MAX_SPEED)    m2Speed = MAX_SPEED;
  motors.setSpeeds(m1Speed, m2Speed);
}
