const int TDS_PIN = A0;

// Sensor specs
const float VREF = 5.0;           // Arduino Nano uses 5V as ADC reference
const float TDS_VOLTAGE_MAX = 2.3; // Max output voltage from sensor
const int ADC_RESOLUTION = 1024;  // 10-bit ADC

void setup() {
  Serial.begin(9600);
}

void loop() {
  int analogValue = analogRead(TDS_PIN);
  float voltage = analogValue * (VREF / ADC_RESOLUTION); // Convert to voltage

  // Voltage is in range 0–2.3V
  // TDS sensor typically uses: TDS (ppm) = (voltage / 2.3V) * 1000
  float tds = (voltage / TDS_VOLTAGE_MAX) * 1000.0;

  Serial.print("Raw: ");
  Serial.print(analogValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 3);
  Serial.print(" V | TDS: ");
  Serial.print(tds, 1);
  Serial.println(" ppm");

  delay(100); // 1 reading per second
}
