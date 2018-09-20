int cnt = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  //pinMode(13, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  char s;
  Serial.print(cnt);
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.print(" ");
  Serial.print(random(0,100));
  Serial.println(" ");
  cnt = cnt+1;
  delay(1000);
  
  //if(Serial.available() > 0)
  //{
    //if(Serial.read() == '1')
    //{
      //digitalWrite(13, HIGH);
    //}
    //if(Serial.read() == '0')
    //{
      //digitalWrite(13, LOW);
    //}
  //}
}
