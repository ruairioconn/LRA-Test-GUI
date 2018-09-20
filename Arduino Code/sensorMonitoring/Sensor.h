#ifndef SENSOR_H
#define SENSOR_H

#include "Arduino.h"

class Sensor
{
  static int readAnalogPin(int pinNumber);
  static int readDigitalPin(int pinNumber, char* pinType);
  
  public:
  Sensor(char* pinType, int pinNumber);

  int readPin();
  void setPinMode(int state);
  char* getType();            // returns the pin type ex: digitalO, digitalI, or analog

  private:
  int pinNumber;
  char* pinType;

  void initPin();             // abstracts way initializing a pin yourself, looks at type and figures it out
};

#endif 
