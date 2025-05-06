#include <Arduino.h>
#include <bmp180.h>
#include <tsl2561.h>
#include <dht11.h>
#include <max4466.h>

double noise, hum, temp, lux, press;

void init_sensors(bool debug)
{
    if (debug){
        Serial.println("______________");
        Serial.println("SENSORS_INIT");
        Serial.println("______________");
    }
    init_bmp(debug);
    init_tsl(debug);
    init_dht(debug);
}

double *read_sensors(bool debug)
{   
    if (debug){
        Serial.println("______________");
        Serial.println("SENSORS_READING");
        Serial.println("______________");
    }
    hum=dht_read_hum(debug);
    temp=dht_read_temp(debug);
    press= bmp_hpa_read(debug);
    lux= tsl_read(debug);
    noise=max_read_noise(debug);

    static double tab[5];
    tab[0]=hum;
    tab[1]=temp;
    tab[2]=press;
    tab[3]=lux;
    tab[4]=noise;

    if (debug){
        Serial.print(tab[0]);
        Serial.print('\t');
        Serial.print(tab[1]);
        Serial.print('\t');
        Serial.print(tab[2]);
        Serial.print('\t');
        Serial.print(tab[3]);
        Serial.print('\t');
        Serial.println(tab[4]);
        Serial.println("success");
    }

    return tab;
}

void print_sensors()
{

}