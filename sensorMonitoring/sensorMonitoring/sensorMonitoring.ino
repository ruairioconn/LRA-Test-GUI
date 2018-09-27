#include "constants.h"
#include "Timer.h"

char incomingString[200];         // a String to hold incoming data
bool stringReceived = false;  // whether the string is complete

unsigned long previousLog = millis();
bool takeLog = true;
int currentIndex = 0;
Timer t;

void ignite();

void setup() 
{
  Serial.begin(BAUD_RATE);
  initTimer();
}

void loop() 
{
  if(stringReceived)
  {
    noInterrupts();
    handleCommand();
    stringReceived = false;
    interrupts();
  }
}

void logSensors()
{
  for(uint8_t sensorNum = 0; sensorNum < NUM_SENSORS; sensorNum++)
  {
    int reading = sensors[sensorNum].readPin(); 
    Serial.print(reading);
    if(sensorNum != NUM_SENSORS - 1){Serial.print(",");}
  }
  Serial.print("\n");
}

void initTimer()
{ 
  // initialize timer1 
  noInterrupts();           // disable all interrupts
  TCCR1A = 0;               // clear compare capture registers
  TCCR1B = 0;               // clear compare capture regusters
  TCNT1  = 0;               // reset timer to count to 0

  float desiredFrequency = 1.0 / (float)(TIME_BETWEEN_READINGS_IN_MILLISECONDS / 1000.0);
  OCR1A = (int)(16000000 / 1024 / desiredFrequency);             // compare match register 16MHz/prescaler/2Hz
  TCCR1B |= (1 << WGM12);                 // CTC mode
  TCCR1B |= (1 << CS12) | (1 << CS10);    // 1024 prescaler 
  TIMSK1 |= (1 << OCIE1A);                // enable timer compare interrupt with register A
  interrupts();                           // enable all interrupts
}

ISR(TIMER1_COMPA_vect)          // timer compare interrupt service routine
{
  noInterrupts();
  if(takeLog)
  {
    logSensors();
  }
  interrupts();
}

void handleCommand()
{
  //Serial.print("Command received: ");
  //Serial.println(incomingString);
  if(strcmp(incomingString, "stop") == 0)
  {
    takeLog = false;
  }
  else if(strcmp(incomingString, "start") == 0)
  {
    takeLog = true;
  }
  else if(strcmp(incomingString, "WV2") == 0)
  {
   if(sensors[WV2_INDEX].readPin() == LOW) {sensors[WV2_INDEX].setPinMode(HIGH);}
   else {sensors[WV2_INDEX].setPinMode(LOW);}
  }
  else if(strcmp(incomingString, "OV4") == 0)
  {
   if(sensors[OV4_INDEX].readPin() == LOW) {sensors[OV4_INDEX].setPinMode(HIGH);}
   else {sensors[OV4_INDEX].setPinMode(LOW);}
  }
  else if(strcmp(incomingString, "OV5") == 0)
  {
   if(sensors[OV5_INDEX].readPin() == LOW) {sensors[OV5_INDEX].setPinMode(HIGH);}
   else {sensors[OV5_INDEX].setPinMode(LOW);}
  }
  else if(strcmp(incomingString, "NV2") == 0)
  {
   if(sensors[NV2_INDEX].readPin() == LOW) {sensors[NV2_INDEX].setPinMode(HIGH);}
   else {sensors[NV2_INDEX].setPinMode(LOW);}
  }
  else
  {
    Serial.println("Unknown Command");
    return;
  }
}

void serialEvent() 
{
  while (Serial.available()) 
  {
    // get the new byte:
    char inChar = (char)Serial.read();
 
    if (inChar == '\n') //incoming commands are delimmited by the new line character
    {
      stringReceived = true;
      incomingString[currentIndex] = '\0';
      currentIndex = 0;
    }
    else
    {
      incomingString[currentIndex++] = inChar;
    }
  }
}
