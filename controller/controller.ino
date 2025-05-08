/*
* Fil: controller.ino
* Creator: Lucas Norrflod
* Date: 3/4-2025
* This code use a gyroscope and get the y- and x-axis transferred to a ruby program
*/

//included libraries
#include "Wire.h"
#include <MPU6050_light.h>

MPU6050 mpu(Wire);

// declare variables
int buttonPress = 0;
int angleX;
int angleY;
String message;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Wire.begin();

  byte status = mpu.begin();
  while (status != 0) {}  // stop everything if could not connect to MPU6050
}

void loop() {
  // put your main code here, to run repeatedly:
  buttonPress = 0;
  if (digitalRead(13) == HIGH) {
    buttonPress = 1;
  }

  // Gets the tilt angle and button input and makes it into a string
  mpu.update();
  angleX = mpu.getAngleX();
  angleY = mpu.getAngleY();
  message = String(angleX) + " " + String(angleY) + " " + String(buttonPress);
  Serial.println(message); //String is printed in the serial port
}
