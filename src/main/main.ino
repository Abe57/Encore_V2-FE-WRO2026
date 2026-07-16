#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <ServoEasing.hpp>
#include <Ultrasonic.h>

// get EVERYTHING

TaskHandle_t Sensors = NULL;
TaskHandle_t Controls = NULL;

// initialize loop objects

Ultrasonic uLeft(32,33);
Ultrasonic uCenter(4,16);
Ultrasonic uRight(17,5);

int left = 0;
int center = 0;
int right = 0;

// initialize proximity sensors
//        LEFT  CENTER  RIGHT
// TRIG |  32  |   4  |  17  |
// ECHO |  33  |  16  |   5  |

int dMin = 20;
int dMax = 150;
int cw = 0;

#define MAX_TURN 40

float rotX = 0;
Adafruit_BNO055 gyro = Adafruit_BNO055(55);
sensors_event_t event;

// initialize BNO055 rotational sensor and related

#define BUTTON 23

// start button

#define PWM 25
#define FW 26
#define BW 27

// motor control pins

int servo_c = 90;
ServoEasing Timonteo; //como te odio serbastian

// initialize servo

int ini_angle = 0;
int angToMatch = 0;
int turnOffset = 0;

// variables for direction algorithm

void getSensors(void * parameters){
  gyro.getEvent(&event);
  ini_angle = event.orientation.x;
  // get initial robot rotation

  for (;;){
    gyro.getEvent(&event);
    rotX = event.orientation.x;

    Serial.print("Gyro roll: ");Serial.println(rotX);
    Serial.println("----------------------------------");

    left = uLeft.read();
    center = uCenter.read();
    right = uRight.read();

    Serial.print("Left prox: ");Serial.print(left);Serial.println("cm");
    Serial.print("Center prox: ");Serial.print(center);Serial.println("cm");
    Serial.print("Right prox: ");Serial.print(right);Serial.println("cm");

    angToMatch = ini_angle + (turnOffset*90*cw);

    delay(50);
  }
}

void control(void * parameters){
  digitalWrite(FW,HIGH);
  digitalWrite(PWM,HIGH);
  for (;;){
    while (center > dMin){
      if (cw == 0){
        if (left > dMax){
          cw = 1;
          Serial.println("Going clockwise");
        }
        if (right > dMax){
          cw = -1;   
          Serial.println("Going counter-clockwise");
        }
      }
      // the totally awesome algorithm
      Timonteo.easeTo(constrain(servo_c + rotX - angToMatch,servo_c-MAX_TURN,servo_c+MAX_TURN));
      delay(100);
    }
    turnOffset++;
    Timonteo.easeTo(servo_c+(MAX_TURN*cw));
    Serial.println("wall detected: turn...NOW!!!!");
    while (rotX <= angToMatch) {
      delay(50);
    }
    Serial.println("We good now, keep going");
  }
}

void setup() {
  Serial.begin(115200);

  if (!gyro.begin()) {
    Serial.println("Could not find BNO055.");
    while(1);
  }
  gyro.setExtCrystalUse(true);

  Timonteo.attach(18, 90);
  Timonteo.setSpeed(170);

  pinMode(BUTTON, INPUT_PULLUP);

  pinMode(PWM, OUTPUT);
  pinMode(FW, OUTPUT);
  pinMode(BW, OUTPUT);

  Serial.println("Press button to start");
  while (digitalRead(BUTTON) == HIGH)
  {
    delay(1);
  }

  xTaskCreatePinnedToCore(
    control,
    "Car Control",
    4096,
    NULL,
    10,
    &Controls,
    1
  );
  // start control thread on core 1

  xTaskCreatePinnedToCore(
    getSensors,
    "Sensor Data",
    4096,
    NULL,
    1,
    &Sensors,
    0
  );
  // start sensors thread on core 0
}

void loop() {
}
