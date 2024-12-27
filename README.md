Automatic Target Tracking System

Overview:
This project integrates machine learning, computer vision, and mechanical systems to create an automated object-tracking system. Using YOLO (You Only Look Once) for object detection, the system tracks specific objects in real-time and adjusts its motorized hardware to follow targets.

Files and Structure:
- arduino/MoveStepper.ino: Arduino code for controlling the stepper motor.
- python/: Contains Python code and dependencies for object detection.
  - human_detection.py: Python script for YOLO-based object detection.
  - requirements.txt: Lists the Python dependencies required for the project.
- stl/Housing + Components.stl: STL file for 3D-printed housing and hardware components.
- LICENSE: License file specifying the project’s terms of use.

Setup and Usage:
1. Install Dependencies:
   Run the following command to install Python dependencies:
   pip install -r requirements.txt

2. Upload Arduino Code:
   - Open MoveStepper.ino in the Arduino IDE.
   - Connect your microcontroller (e.g., Elegoo Mega 2560).
   - Select the appropriate COM port and board in the Arduino IDE.
   - Upload the code to the microcontroller.

3. Run the Python Script:
   - Ensure your camera (e.g., Logitech C615) is connected to your computer.
   - Run the Python script:
     python human_detection.py

Hardware Requirements:
- Microcontroller: Elegoo Mega 2560
- Stepper Motor: 28BYJ-48 with ULN2003 Driver
- Camera: Logitech C615 or equivalent
- 3D Printer: Sovol SV06 Plus (or similar)

Demo:
Watch the system in action: *INSERT LINK HERE*

Documentation:
Detailed documentation for this project is available here: [Link to e-portfolio]

Future Improvements:
1. Implement edge computing using a Raspberry Pi for standalone functionality.
2. Add a dynamic speed control mechanism to improve tracking smoothness.
3. Expand tracking capabilities with a pan-tilt mechanism for 2D coverage.

License:
This project is licensed under the MIT License. See the LICENSE file for more details.
