# 1 "F:\\Logiciels\\Arduino_graphique\\Blockly-rduino-communication\\scripts\\rDuino\\blockly_upload_temp\\blockly_upload_temp.ino"
# 1 "F:\\Logiciels\\Arduino_graphique\\Blockly-rduino-communication\\scripts\\rDuino\\blockly_upload_temp\\blockly_upload_temp.ino"
void setup() {
  pinMode(10, 0x1);
}

void loop() {
  digitalWrite(10, 0x1);
  delay(1000);
  digitalWrite(10, 0x0);
  delay(1000);

}
