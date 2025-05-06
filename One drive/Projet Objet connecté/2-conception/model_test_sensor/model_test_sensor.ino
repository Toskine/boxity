/*
 * This is the main script, where the function is tested.
 */
 
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Sensor_initialisation();

}

void loop() {
  // put your main code here, to run repeatedly:
  Sensor_sample();
  delay(1000);

}
