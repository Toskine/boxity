#include "DHT.h"
#define DHTPIN D6
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void init_dht(bool debug)
{
    dht.begin();
}

float dht_read_hum(bool debug)
{
    float h = dht.readHumidity();

    if (debug)
    {
        Serial.println("humidity = " + String(h) + "%");
    }
    return h;
}

float dht_read_temp(bool debug)
{

    float t = dht.readTemperature();

    if (debug)
    {
        Serial.println("temperature = " + String(t) + "°C");
    }
    return t;
}