#ifndef CONSTANTS_H
#define CONSTANTS_H

#include "Arduino.h"
#include "Sensor.h" 

#define BAUD_RATE 9600
#define TIME_BETWEEN_READINGS_IN_MILLISECONDS 1000 

#define NUM_SENSORS 13

Sensor sensors[13] = { {"digitalI", 6} , {"digitalI", 7} , {"digitalI", 8} , {"digitalI", 9} , {"analog", A0} , {"analog", A1} , {"analog", A2} , {"analog", A3} , {"analog", A4} , {"digitalO", 2} , {"digitalO", 3} , {"digitalO", 4} , {"digitalO", 5} };

#define WV2_INDEX 11

#define OV4_INDEX 12
#define OV5_INDEX 9

#define NV2_INDEX 10

#endif
