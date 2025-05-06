#include <Adafruit_NeoPixel.h>

#define LED_PIN  13
#define LED_COUNT  4
#define BRIGHTNESS 0.1

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void init_strip()
{
  strip.begin();
}

void strip_off()
{
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
}

void strip_on(unsigned int red,unsigned int green,unsigned int blue)
{
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(red*BRIGHTNESS, green*BRIGHTNESS, blue*BRIGHTNESS));
  }
  strip.show();
}

void strip_set(unsigned int n ,unsigned int red,unsigned int green,unsigned int blue)
{
  strip.setPixelColor(n, strip.Color(red*BRIGHTNESS, green*BRIGHTNESS, blue*BRIGHTNESS));
  strip.show();
}



unsigned long timer=millis();
bool strip_stat=false;
unsigned int G;
unsigned int R;
unsigned int B;

void strip_blink(unsigned int periode,unsigned int red,unsigned int green,unsigned int blue)
{
  if(millis()-timer>=periode)
  { 
    strip_stat= !strip_stat;
    G=strip_stat*green*BRIGHTNESS;
    R=strip_stat*red*BRIGHTNESS;
    B=strip_stat*blue*BRIGHTNESS;

    for(int i=0; i<LED_COUNT; i++) 
    {
    strip.setPixelColor(i, strip.Color(R,G,B));
    }
    strip.show();
    timer=millis();
  }
}

unsigned int dt = 3000;
unsigned int move = random(0,1);
unsigned int p=random(1,4);

void strip_demo()
{ 
  if(millis()-timer>=dt)
  { 
    strip_off();
    move = random(0,1);
    p=random(1,4);
    G=random(0,255)*BRIGHTNESS;
    R=random(0,255)*BRIGHTNESS;
    B=random(0,255)*BRIGHTNESS;
    timer=millis();
  }

  if(move==0)
  {
    float br= (pow(sin(0.5*2*PI*(millis()-timer)/float(1000)),p)+1)/2;
    for(int i=0; i<LED_COUNT; i++) 
    {
    strip.setPixelColor(i, strip.Color(R*br,G*br,B*br));
    }
    strip.show();
  }
}