#include <Arduino.h>

void init_blinkLED(){
    pinMode(LED_BUILTIN,OUTPUT);
    digitalWrite(LED_BUILTIN,HIGH);
}

unsigned long blink_timer=millis();

void blinkLED(unsigned int periode)
{
  if(millis()-blink_timer>=periode)
  {
    digitalWrite(LED_BUILTIN,!digitalRead(LED_BUILTIN));
    blink_timer=millis();
  }
}