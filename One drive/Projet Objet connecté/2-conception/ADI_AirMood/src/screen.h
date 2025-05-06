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

bool screen_status=false;

void init_screen(bool debug)
{
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) // Address 0x3D for 128x64
  { 
   screen_status=false;
  }
  else
  {
    {
      screen_status=true;
      display.clearDisplay();
    }
  }  
}
void screen_add_text(unsigned int size, unsigned int x, unsigned int y, String txt)
{
  display.setTextSize(size);
  display.setTextColor(WHITE);
  display.setCursor(x, y);
  display.print(txt);
}

void screen_print()
{
  display.display();
}

void screen_clear()
{
  display.clearDisplay();
  display.display();
}

void screen_demo(){
  
   //code to initialise the sensor
  display.setTextSize(2);
  display.setTextColor(WHITE);

  display.setCursor(0, 10);

  
  // Display static text
  display.print("hello word");
  //display.display();
}

String prev_status= "";

void display_status(String status)
{
  if (prev_status!=status)
    { 
      screen_clear();
      screen_add_text(2, 0, 20, "Status :");
      screen_add_text(1, 0, 50, status);
      screen_print();
      prev_status=status;
    }
}
