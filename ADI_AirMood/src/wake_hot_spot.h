#include <Arduino.h>

#define Bp_pin 14
#define button_push_duration 2000

void init_bp()
{
    pinMode(Bp_pin, INPUT_PULLUP);
}

bool test_button()
{
    
    return !digitalRead(Bp_pin);
}