#include <Wire.h>
#include <Adafruit_BMP085.h>
Adafruit_BMP085 bmp;

void init_bmp(bool debug){
  bmp.begin();
  if(debug and !bmp.begin()){
  Serial.println("Could not find a valid BMP085 sensor, check wiring!");
  while (1);
  }
}
 
float bmp_hpa_read(bool debug){
  hpa = bmp.readPressure();
  hpa = hpa/100;
  if(debug){
    Serial.print("Pression = "+hpa+"hpa");
    Serial.println(" Pa");
    Serial.println("-------------------------------------------");
  }
  return hpa;
}
