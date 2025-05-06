#include "DHT.h"           // inclure la librairie
#define DHTPIN 33          // déclarer le pin
#define DHTTYPE DHT11      // définir le capteur qui est ici un dht11
DHT dht(DHTPIN, DHTTYPE);  // déclarer le capteur avec la librairie

void init_dht(bool debug){
  dht.begin();//initialisation du capteur
}

float dht_temp_read(bool debug){
  float t = dht.readTemperature();  // calcul de la température
  if (debug){
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println("°C ");
  Serial.println("-------------------------------------------");
  }
  return t;
}

float dht_hum_read(bool debug){
  float h = dht.readHumidity();  // calcul de l'humidité
  if (debug){
  Serial.print("Humidity: ");      
  Serial.print(h);
  Serial.print("%");
  Serial.println("-------------------------------------------");
  }
  return h;
}
