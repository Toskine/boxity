#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>

Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

void init_tsl(bool debug)
{

    if (!tsl.begin())
    {
        /* There was a problem detecting the TSL2561 ... check your connections */
        Serial.print("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
        while (1)
            ;
    }
    tsl.enableAutoRange(true); /* Auto-gain ... switches automatically between 1x and 16x */

    //tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS); /* fast but low resolution */
                                                          // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);  /* medium resolution and speed   */
     tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  /* 16-bit data but slowest conversions */
}

float tsl_read(bool debug)
{

    sensors_event_t event;
    tsl.getEvent(&event);

    /* Display the results (light is measured in lux) */
    float lux = event.light;
    if (debug)
    {
        Serial.print(String(lux));
        Serial.println(" lux");
    }
    return lux;
}
