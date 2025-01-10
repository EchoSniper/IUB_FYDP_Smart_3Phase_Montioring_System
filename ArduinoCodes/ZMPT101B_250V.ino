#include <ZMPT101B.h>

#define SENSITIVITY 370.0f

// Define voltage sensors for each phase
ZMPT101B voltageSensorA(A4, 50.0);  // Phase A
ZMPT101B voltageSensorB(A5, 50.0);  // Phase B
ZMPT101B voltageSensorC(A6, 50.0);  // Phase C

void setup() {
  Serial.begin(9600);
  
  // Set sensitivity for each sensor
  voltageSensorA.setSensitivity(SENSITIVITY);
  voltageSensorB.setSensitivity(SENSITIVITY);
  voltageSensorC.setSensitivity(SENSITIVITY);
}

void loop() {
  // Read the RMS voltage for each phase
  float voltageA = voltageSensorA.getRmsVoltage() -20;
  float voltageB = voltageSensorB.getRmsVoltage()-28;
  float voltageC = voltageSensorC.getRmsVoltage()-28;

  // Print the voltages for each phase
  Serial.print("Phase A: ");
  Serial.println(voltageA);
  
  Serial.print("Phase B: ");
  Serial.println(voltageB);
  
  Serial.print("Phase C: ");
  Serial.println(voltageC);

}
