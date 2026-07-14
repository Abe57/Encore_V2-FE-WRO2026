#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <ServoEasing.hpp>
#include <Ultrasonic.h>


TaskHandle_t Sensors = NULL;
TaskHandle_t Controls = NULL;

Ultrasonic uLeft(32,33);
Ultrasonic uCenter(2,16);
Ultrasonic uRight(17,5);

float left = 0;
float center = 0;
float right = 0;

Adafruit_BNO055 gyro = Adafruit_BNO055(55);

#define M_LEFT = 26;
#define M_RIGHT = 27;

ServoEasing Timonteo;

void getSensors(void * parameters){
  for (;;){
    Serial.println("Getting sensor data");

    sensors_event_t event;
    gyro.getEvent(&event);

    float rotZ = event.orientation.z;
    
    left = uLeft.read(CM);
    center = uCenter.read(CM);
    right = uRight.read(CM);

    delay(100);
  }
}

void control(void * parameters){
  for (;;){
    Serial.println("Handling direction");
    delay(2000);
  }
}

void setup() {
  Serial.begin(115200);

  gyro.begin();
  gyro.setExtCrystalUse(true);

  Timonteo.attach(18, 90);

  xTaskCreatePinnedToCore(
    getSensors,
    "Sensor Data",
    2048,
    NULL,
    2,
    &Sensors,
    0
  );

  xTaskCreatePinnedToCore(
    control,
    "Car Control",
    1024,
    NULL,
    1,
    &Controls,
    1
  );
}

void loop() {
}
