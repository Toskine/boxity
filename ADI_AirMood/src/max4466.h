#include <Arduino.h>

#define MaxPin A0

void init_max(bool debug)
{
}

float max_read_noise(bool debug)
{
    unsigned long t0 = millis();
    unsigned long dt = 500; // ms
    int max = 0;
    int min = 1023;
    int val;

    while (millis() - t0 < dt)
    {
        val = analogRead(MaxPin);
        if (val < 1025)
        {
            if (val > max)
            {
                max = val;
            }
            else if (val < min)
            {
                min = val;
            }
        }
    }

    int peakToPeak = max - min;

    float v = peakToPeak / (float)pow(2, 10) * 3.3;
    int db= map(1000*v,2200,2510,65,95);

    if (debug)
    {
        Serial.println("dB = " + String(db) + "dB");
    }
    return db;
}