#ifndef CONSTANTS_H
#define CONSTANTS_H

#include "Arduino.h"
#include "Sensor.h" 

/*  The point of this file is to abstract out the main constants that need to be changed for this code to work on other similar boards as well.
 *  So if we wanted to use this on a board that needed faster output bandwidth, or more sensors, or more solenoids we could do that with only 
 *  a few constant changes in this file.
 */ 

#define BAUD_RATE 9600
#define DESIRED_FREQUENCY_BETWEEN_READINGS 1 // In HZ, can go below one just make sure you'd specify it with a zero in front EX: 0.125 

#define NUM_SENSORS 11   // number of interfaceable modules on the board

Sensor sensors[11] = { {"digitalI", 6} , {"digitalI", 7} , {"digitalI", 8} , {"digitalI", 9} , {"analog", A2} , {"analog", A3} , {"analog", A4} , {"digitalO", 2} , {"digitalO", 3} , {"digitalO", 4} , {"digitalO", 5} };

#define SOLENOID_INDEX 6 // The solenoids do not have zero indexing, so start this one before the actual first index of the solenoids

#endif
