#include <Filters.h>

float testFrequency = 50;
int SensorA = 0, SensorB = 0, SensorC = 0;
float intercept = 0.7;
float slope = 0.04;
float current_VoltsA, current_VoltsB, current_VoltsC;

void setup() {
  Serial.begin(9600);  // Start serial communication at 9600 baud rate
  Serial.println("Voltage Readings:");
}

void loop() {
  RunningStatistics inputStatsA, inputStatsB, inputStatsC;

  while (true) {
    // Read sensor values for phases A, B, and C
    SensorA = analogRead(A4);
    SensorB = analogRead(A5);
    SensorC = analogRead(A6);

    // Process sensor inputs for each phase
    inputStatsA.input(SensorA);
    inputStatsB.input(SensorB);
    inputStatsC.input(SensorC);

    // Calculate voltages for each phase
    current_VoltsA = intercept + slope * inputStatsA.sigma();
    current_VoltsB = intercept + slope * inputStatsB.sigma();
    current_VoltsC = intercept + slope * inputStatsC.sigma();

    current_VoltsA = current_VoltsA * 40.3231 - 20;
    current_VoltsB = current_VoltsB * 40.3231 - 20;
    current_VoltsC = current_VoltsC * 40.3231 - 30;

    // Print voltages for each phase
    Serial.print("Phase A Voltage: ");
    Serial.print(current_VoltsA);
    Serial.println("V");

    Serial.print("Phase B Voltage: ");
    Serial.print(current_VoltsB);
    Serial.println("V");

    Serial.print("Phase C Voltage: ");
    Serial.print(current_VoltsC);
    Serial.println("V");
  }
}
