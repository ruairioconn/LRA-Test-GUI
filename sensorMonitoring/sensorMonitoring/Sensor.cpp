#include "sensor.h"

Sensor::Sensor(char *pinType, int pinNumber)
{
  this->pinType = pinType;
  this->pinNumber = pinNumber;
  this->initPin();
}

void Sensor::initPin()
{
  if(strcmp(this->pinType, "digitalI") == 0)
  {
    pinMode(this->pinNumber, INPUT);
  }
  else if(strcmp(this->pinType, "digitalO") == 0)
  {
    pinMode(this->pinNumber, OUTPUT);
  }
  else if(strcmp(this->pinType, "analog") == 0)
  {
    return; //this->analog pins don't need setup
  } 
  else
  {
    Serial.println("Unknown Pin Type!");
    //unknown pin type!! This is bad!!
  }
}

char* Sensor::getType()
{
  return this->pinType;
}

int Sensor::readDigitalPin(int pinNumber, char* type)
{
  if(strcmp(type, "digitalO") == 0)
  {
    if(pinNumber <= 7 ) {return bitRead(PORTD, pinNumber);}
    else{return bitRead(PORTB, pinNumber);}
  }
  else
  {
    return digitalRead(pinNumber);
  }
}

int Sensor::readAnalogPin(int pinNumber)
{
  float reading = analogRead(pinNumber);
  float readingInVolts = reading / 256.0;
  int readingInMiliVolts = readingInVolts * 1000;
  return readingInMiliVolts;
}

int Sensor::readPin()
{
  if(strcmp(this->getType(), "digitalO") == 0 || strcmp(this->getType(), "digitalI") == 0)
  {
    return Sensor::readDigitalPin(this->pinNumber, this->pinType);
  }
  else
  {
    return Sensor::readAnalogPin(this->pinNumber);
  }
}

void Sensor::setPinMode(int state)
{
  if(strcmp(this->getType(), "digitalO") == 0)
  {
    digitalWrite(this->pinNumber, HIGH);
  }
}

