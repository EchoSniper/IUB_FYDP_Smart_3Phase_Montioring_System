#include <ZMPT101B.h>

#define SENSITIVITY 370.0f

// Define voltage sensors for each phase
ZMPT101B voltageSensorA(A4, 50.0);  // Phase A
ZMPT101B voltageSensorB(A5, 50.0);  // Phase B
ZMPT101B voltageSensorC(A6, 50.0);  // Phase C

// Pin assignments for ACS712 sensors
const int sensorPinA = A3;  // Phase A
const int sensorPinB = A2;  // Phase B
const int sensorPinC = A1;  // Phase C
const int sensorPinG = A0;  // Ground

// Variables to store voltage and current readings
float voltageA, voltageB, voltageC;
float currentA, currentB, currentC, currentG;

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  
  // Set sensitivity for each voltage sensor
  voltageSensorA.setSensitivity(SENSITIVITY);
  voltageSensorB.setSensitivity(SENSITIVITY);
  voltageSensorC.setSensitivity(SENSITIVITY);
}

void loop() {
  // Read the RMS voltage for each phase, applying offsets
  voltageA = voltageSensorA.getRmsVoltage() - 20;
  voltageB = voltageSensorB.getRmsVoltage() - 28;
  voltageC = voltageSensorC.getRmsVoltage() - 28;

  // Read raw sensor values from each phase
  int sensorValueA = analogRead(sensorPinA);
  int sensorValueB = analogRead(sensorPinB);
  int sensorValueC = analogRead(sensorPinC);
  int sensorValueG = analogRead(sensorPinG);

  // Convert sensor values to voltage (assuming 5V reference)
  float voltageA_raw = (sensorValueA * 5.0) / 1023.0;
  float voltageB_raw = (sensorValueB * 5.0) / 1023.0;
  float voltageC_raw = (sensorValueC * 5.0) / 1023.0;
  float voltageG_raw = (sensorValueG * 5.0) / 1023.0;

  // Convert voltage to current for each phase (ACS712 5A version)
  currentA = (voltageA_raw - 2.5) * 8 + 3.10;
  currentB = (voltageB_raw - 2.5) * 8;
  currentC = (voltageC_raw - 2.5) * 8;
  currentG = (voltageG_raw - 2.5) * 8;

  // Print current and voltage readings on the same line
  Serial.print(currentG, 2);   // Ground current
  Serial.print(", ");
  Serial.print(currentA, 2);   // Phase A current
  Serial.print(", ");
  Serial.print(currentB, 2);   // Phase B current
  Serial.print(", ");
  Serial.print(currentC, 2);   // Phase C current
  Serial.print(", ");
  Serial.print(voltageA, 2);   // Phase A voltage
  Serial.print(", ");
  Serial.print(voltageB, 2);   // Phase B voltage
  Serial.print(", ");
  Serial.println(voltageC, 2); // Phase C voltage
}
