#ifndef CONSTANTS_H
#define CONSTANTS_H

#include "Arduino.h"
#include "Sensor.h" 

#define BAUD_RATE 9600
#define TIME_BETWEEN_READINGS_IN_MILLISECONDS 1000 

#define NUM_SENSORS 11

Sensor sensors[11] = { {"digitalI", 6} , {"digitalI", 7} , {"digitalI", 8} , {"digitalI", 9} , {"analog", A2} , {"analog", A3} , {"analog", A4} , {"digitalO", 2} , {"digitalO", 3} , {"digitalO", 4} , {"digitalO", 5} };

#define WV2_INDEX 9

#define OV4_INDEX 10
#define OV5_INDEX 7

#define NV2_INDEX 8

#endif
