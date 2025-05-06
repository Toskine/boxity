 
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_dht(true);

}

void loop() {
  // put your main code here, to run repeatedly:
  dht_temp_read(true);
  dht_hum_read(true);
  delay(1000);

}
