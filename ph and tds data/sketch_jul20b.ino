const int pH_pin = A0;
float voltage, pH;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(pH_pin);           // 10-bit ADC: 0–1023
  float voltage = analogRead(A0) * (5.0 / 1024.0);
  float pH = -5.70 * voltage + 30.4;  // example: adjust based on two real measurements


  Serial.print("Voltage: ");
  Serial.print(voltage, 3);
  Serial.print(" V\tpH: ");
  Serial.println(pH, 2);

  delay(100);  // Sample every 1 second
}
