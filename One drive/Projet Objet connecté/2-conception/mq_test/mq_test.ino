
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_mq(true);

}

void loop() {
  // put your main code here, to run repeatedly:
  mq_co2_read(true);
  delay(1000);

}
