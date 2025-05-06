#include <Wire.h>
#include "TSL2561.h"
TSL2561 tsl(TSL2561_ADDR_FLOAT);

void init_tsl(bool debug) {
  tsl.begin()
  if (tsl.begin() and debug) {
    Serial.println("Found sensor");
  } else {
    Serial.println("No sensor?");
    while (1);
  }
  tsl.setGain(TSL2561_GAIN_16X);      // set 16x gain (for dim situations)
  tsl.setTiming(TSL2561_INTEGRATIONTIME_13MS);  // shortest integration time (bright light)
}

float tsl_lux_read(bool debug) {
  
  uint16_t x = tsl.getLuminosity(TSL2561_VISIBLE);
  uint32_t lum = tsl.getFullLuminosity();
  uint16_t ir, full;
  ir = lum >> 16;
  full = lum & 0xFFFF;
  lux = full-ir;

if(debug){
  Serial.print(x, DEC);
  Serial.print("\t"); 
  Serial.print("Visible: "+(full-ir)+"lux");  
  Serial.println("-------------------------------------------");
}
  
