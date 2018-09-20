#include "constants.h"
#include "Timer.h"

char incomingString[200];         // a String to hold incoming data from the serial connection, fills up when a serial event irq triggers
int currentIndex = 0;             // the spot in the incoming string buffer we are at while filling up from the user
bool stringReceived = false;      // whether the string is complete and should be processed, is set by the serial event irq trigger when a \n is received

bool takeLog = true;              // if set false by a stop command coming in from the user, the sensor string will no longer be output periodically back to the user
Timer t;                          

void setup() 
{
  Serial.begin(BAUD_RATE);
  initTimer();
}

void loop() 
{
  if(stringReceived)
  {
    noInterrupts();               // We turn off interrupts so that the Serial event can't trigger and overwrite our command before we process it
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
    if(sensorNum != NUM_SENSORS - 1){Serial.print(",");}      // Don't print a comma after the last sensor reading
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

  OCR1A = (int)(16000000 / 1024 / DESIRED_FREQUENCY_BETWEEN_READINGS);     // compare match register 16MHz/prescaler/2Hz
  TCCR1B |= (1 << WGM12);                 // CTC mode
  TCCR1B |= (1 << CS12) | (1 << CS10);    // 1024 prescaler 
  TIMSK1 |= (1 << OCIE1A);                // enable timer compare interrupt with register A
  interrupts();                           // enable all interrupts
}

ISR(TIMER1_COMPA_vect)          // timer compare interrupt service routine
{
  noInterrupts();               // Preventing any interrupts from stopping us mid log and changing our results
  if(takeLog)
  {
    logSensors();
  }
  interrupts();
}

void handleCommand()
{
  Serial.print("Command received: ");
  Serial.println(incomingString);
  if(strcmp(incomingString, "stop") == 0)
  {
    takeLog = false;
  }
  else if(strcmp(incomingString, "start") == 0)
  {
    takeLog = true;
  }
  else if(incomingString[0] == 'S' && incomingString[1] == 'O' && incomingString[2] == 'L')
  {
    char solNumberAsChar = incomingString[3];
    int solNumber = solNumberAsChar - '0';
    sensors[SOLENOID_INDEX + solNumber].setPinMode(HIGH);
  }
  else
  {
    Serial.println("Unknown Command");
    return;
  }
}

void serialEvent() 
{
  while (Serial.available() && !stringReceived)           // if a string has been received we don't want the serialEvent handler to overwrite our data before we process it
  {
    // get the new byte:
    char inChar = (char)Serial.read();
 
    if (inChar == '\n') //incoming commands are delimmited by the new line character and will signal a full command has been received
    {
      stringReceived = true;
      incomingString[currentIndex] = '\0';    //adding on the null character at the end
      currentIndex = 0;
    }
    else
    {
      incomingString[currentIndex++] = inChar;
    }
  }
}
