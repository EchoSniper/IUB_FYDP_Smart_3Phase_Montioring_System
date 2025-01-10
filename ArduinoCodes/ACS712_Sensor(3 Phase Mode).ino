// Pin assignments for ACS712 sensors
const int sensorPinA = A3;  // Phase A
const int sensorPinB = A2;  // Phase B
const int sensorPinC = A1;  // Phase C
const int sensorPinG = A0;  // Ground 


// Variables to store voltage and current readings
float voltageA, currentA;
float voltageB, currentB;
float voltageC, currentC;
float voltageG, currentG;

void setup() {
  Serial.begin(9600);  // Initialize serial communication
}

void loop() {
  // Read raw sensor values from each phase
  int sensorValueA = analogRead(sensorPinA);
  int sensorValueB = analogRead(sensorPinB);
  int sensorValueC = analogRead(sensorPinC);
  int sensorValueG = analogRead(sensorPinG);

  // Convert sensor values to voltage (assuming 5V reference)
  voltageA = (sensorValueA * 5.0) / 1023.0;
  voltageB = (sensorValueB * 5.0) / 1023.0;
  voltageC = (sensorValueC * 5.0) / 1023.0;
  voltageG = (sensorValueC * 5.0) / 1023.0;

  // Convert voltage to current for each phase (ACS712 5A version)
  currentA = (voltageA - 2.5) * 8 + 3.10;
  currentB = (voltageB - 2.5) * 8;
  currentC = (voltageC - 2.5) * 8;
  currentG = (voltageC - 2.5) * 8;
  //CSV Format (easy for serial reading/logging)
Serial.print(currentA, 2);  // Phase A current with 2 decimal precision
Serial.print(",");
Serial.print(currentB, 2);  // Phase B current
Serial.print(",");
Serial.print(currentC, 2);  // Phase C current
Serial.print(",");
Serial.println(currentG, 2);  // Phase G current + new line
}
