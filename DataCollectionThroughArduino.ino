#include <Filters.h> // Library for RMS calculation

// Settings for ZMPT101B Voltage Sensors
float testFrequency = 50; // Frequency (50Hz or 60Hz)
float windowLength = 40.0 / testFrequency; // RMS window length
float voltageIntercepts[] = {-0.04, -0.04, -0.04}; // Calibration intercepts for voltages
float voltageSlopes[] = {0.0405, 0.0405, 0.0405};  // Calibration slopes for voltages
float currentIntercepts[] = {0.0, 0.0, 0.0, 0.0};  // Calibration intercepts for currents
float currentSlopes[] = {0.1, 0.1, 0.1, 0.1};      // Calibration slopes for currents

// Analog Pins
int currentPins[] = {A0, A1, A2, A3}; // Currents: Ground, PhC, PhB, PhA
int voltagePins[] = {A4, A5, A6};     // Voltages: PhA, PhB, PhC

// Calculated values
float phaseCurrents[4]; // Phase currents: Ground, PhC, PhB, PhA
float phaseVoltages[3]; // Phase voltages: PhA, PhB, PhC

unsigned long updateInterval = 5000; // 5 seconds update interval
unsigned long previousMillis = 0;

RunningStatistics voltageStats[3]; // RMS stats for voltages
RunningStatistics currentStats[4]; // RMS stats for currents

void setup() {
  Serial.begin(9600);
  
  // Set up RMS calculation window
  for (int i = 0; i < 3; i++) {
    voltageStats[i].setWindowSecs(windowLength);
  }
  for (int i = 0; i < 4; i++) {
    currentStats[i].setWindowSecs(windowLength);
  }
}

void loop() {
  // Read currents
  for (int i = 0; i < 4; i++) {
    int rawCurrent = analogRead(currentPins[i]);
    currentStats[i].input(rawCurrent);
    phaseCurrents[i] = currentIntercepts[i] + currentSlopes[i] * currentStats[i].sigma();
  }

  // Read voltages
  for (int i = 0; i < 3; i++) {
    int rawVoltage = analogRead(voltagePins[i]);
    voltageStats[i].input(rawVoltage);
    phaseVoltages[i] = voltageIntercepts[i] + voltageSlopes[i] * voltageStats[i].sigma();
    phaseVoltages[i] = phaseVoltages[i] * (40.3231); // Calibration factor
  }

  // Send data every 5 seconds
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= updateInterval) {
    previousMillis = currentMillis;

    // Format: Current_G, Current_C, Current_B, Current_A, Voltage_A, Voltage_B, Voltage_C
    Serial.print(phaseCurrents[0], 2); Serial.print(","); // Ground Current
    Serial.print(phaseCurrents[1], 2); Serial.print(","); // PhC Current
    Serial.print(phaseCurrents[2], 2); Serial.print(","); // PhB Current
    Serial.print(phaseCurrents[3], 2); Serial.print(","); // PhA Current
    Serial.print(phaseVoltages[0], 2); Serial.print(","); // PhA Voltage
    Serial.print(phaseVoltages[1], 2); Serial.print(","); // PhB Voltage
    Serial.println(phaseVoltages[2], 2); // PhC Voltage
  }
}
