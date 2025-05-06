#include <Arduino.h>
#include <screen.h>
#include <strip_led.h>
#include <configure_WiFi.h>
#include <LedBlink.h>
#include <bmp180.h>
#include <tsl2561.h>

#define default_send_freq 200 // envoi / heure


 
bool debug = true;
bool reset_eeprom=false;
String STAT = "STARTING_UP";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(74880);
  pinMode(D8,OUTPUT);
  digitalWrite(D8,HIGH);
  delay(40);
  /*
  
  init_EEPROM(debug);
  init_screen(debug);
  init_blinkLED();
  init_strip();

  delay(100);
  strip_off();
  screen_clear();
  strip_on(255,0,0);

  if (reset_eeprom){reset_EEPROM(debug);}

  STAT = "INIT_CONFIGURING_WIFI";
  while (STAT != "CONNECTION_SUCCESS" and STAT != "configure_WiFi_TIMEOUT" and STAT != "CONNECTION_TIMEOUT")
  {
    configure_WiFi(debug);
    display_status(STAT);
  }
  strip_off();
  delay(10);
  ESP.deepSleep(1000000.0F*float(3600/default_send_freq) - micros());
  delay(1);
  */
 init_bmp(debug);
 init_tsl(debug);
}


unsigned long T1=millis();

void loop() {
  // put your main code here, to run repeatedly:

  bmp_hpa_read(debug);
  tsl_read(debug);
  delay(1000);
}
