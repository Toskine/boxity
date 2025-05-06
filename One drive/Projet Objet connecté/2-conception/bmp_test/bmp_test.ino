
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_bmp(true);

}

void loop() {
  // put your main code here, to run repeatedly:
  bmp_hpa_read(true);
  delay(1000);
}
