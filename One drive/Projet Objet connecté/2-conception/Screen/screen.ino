/*
  description : Code to display text on an OLED I2C screen
  date : 20/01/2022
  auteur : Ines Cabral
*/

// declaration of constants
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void Screen_initialisation(){
  

   if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    while(true){};
    }
    
}

void Screen_display_text(){
  
   //code to initialise the sensor
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);

  
  // Display static text
  display.display(); 
}
