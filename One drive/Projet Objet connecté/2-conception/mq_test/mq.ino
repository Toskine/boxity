#include "MQ135.h"                        //inclure la librairie
const int mq135Pin =  35;                 // Pin sur lequel est branché de MQ135
MQ135 gasSensor = MQ135(mq135Pin);        // declarer le capteur avec la librairie


void init_mq(bool debug){
  float rzero = gasSensor.getRZero();     // Cette valeur doit être remise dans le code du mq135.h à la ligne "R0"
  
  if(debug){
  Serial.print("R0: ");                   // cette valeur sert à initialiser le capteur
  Serial.println(rzero);                  // A savoir que le capteur doit fonctionner 24h avant que les valeurs soient plus précise
  }
}
 
float mq_co2_read(bool debug){
     
  float ppm = gasSensor.getPPM();   // à l'aide de la librairie, --> calcul de la valeur en ppm

  if(debug){
  Serial.print("Co2: ");            // affiche sur le moniteur série la valeur du C0²
  Serial.print(ppm);
  Serial.print("ppm"); 
  Serial.println("-------------------------------------------");  
  }
  return ppm;
}
