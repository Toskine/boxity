#include <Arduino.h>
#include <screen.h>
#include <strip_led.h>
#include <configure_WiFi.h>
#include <LedBlink.h>
#include <wake_hot_spot.h>
#include <sensors.h>
#include <mqtt.h>


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
  
  
  init_EEPROM(debug);
  init_screen(debug);
  init_strip();
  init_bp();

  delay(100);
  strip_off();
  screen_clear();
  strip_on(255,255,255);

  if (reset_eeprom){reset_EEPROM(debug);}

  
  if (test_button())
  {
    STAT = "HOTSPOT_RUNNING";
  }
  else
  {
    STAT = "INIT_CONFIGURING_WIFI";
  }

  while (STAT != "CONNECTION_SUCCESS" and STAT != "configure_WiFi_TIMEOUT" and STAT != "CONNECTION_TIMEOUT")
  {
    configure_WiFi(debug);
    display_status(STAT);
    if(STAT=="HOTSPOT_RUNNING")
    {
      strip_blink(1000,20,20,255);

    }
  }
  strip_off();
  delay(10);
  STAT = "SENSORS_READING";
  display_status(STAT);
  init_sensors(debug);
  mqtt_init(debug);
  double *Data=read_sensors(false);
  mqtt_set_data(Data,false);
  mqttSend(debug);
  
  STAT = "GOING_TO_SLEEP";
  display_status(STAT);
 
  ESP.deepSleep(1000000.0F*float(3600/default_send_freq) - micros());
  delay(1);
  
 
}

void loop() {
  // put your main code here, to run repeatedly:
}
