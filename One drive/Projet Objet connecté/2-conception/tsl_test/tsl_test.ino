
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_tsl(true);

}

void loop() {
  // put your main code here, to run repeatedly:
  tsl_lux_read(true);
  delay(1000);

}
