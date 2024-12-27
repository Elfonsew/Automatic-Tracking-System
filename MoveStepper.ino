#include <Stepper.h>

#define STEPS_PER_REV 2048

const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;

Stepper stepperMotor(STEPS_PER_REV, IN1, IN3, IN2, IN4);

// Variable to store the latest command
char latestCommand = 'S'; // Default to 'S' (stop)

void setup() {
  Serial.begin(9600); // Initialize serial communication
  stepperMotor.setSpeed(5); // Speed in RPM
  Serial.println("Enter R (right), L (left), or S (stop):");
}

void loop() {
  // Check if a new command is available
  if (Serial.available() > 0) {
    char incomingChar = Serial.read(); // Read the latest character

    // Filter out newline and carriage return
    if (incomingChar != '\n' && incomingChar != '\r') {
      latestCommand = incomingChar; // Update the latest command
      Serial.print("Received command: ");
      Serial.println(latestCommand);
    }
  }

  // Execute the latest command
  if (latestCommand == 'R') {
    stepperMotor.step(-1); // Rotate CW
  } else if (latestCommand == 'L') {
    stepperMotor.step(1); // Rotate CCW
  } else if (latestCommand == 'S') {
    // Stop the motor (no action required)
  }
}
