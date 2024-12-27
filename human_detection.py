import torch
import cv2
import warnings
import serial
from ultralytics import YOLO

warnings.filterwarnings("ignore", category=FutureWarning)

# Serial communication setup
arduino = serial.Serial('COM3', 9600)  # Replace 'COM3' with the correct port for your Arduino

# Adjustable screen thresholds for left and right regions
THRESHOLD = 0.425
LEFT_THRESHOLD = THRESHOLD  # Left
RIGHT_THRESHOLD = 1 - THRESHOLD  # Right

# YOLO setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load the YOLO model
model = YOLO("yolo11s.pt")

# Restrict detection to 'person' and 'dog' only
model.classes = [0, 16]  # 0: 'person', 16: 'dog'

# Try external webcam first (index 1), then default camera (index 0)
cap = cv2.VideoCapture(1)  # External webcam
if not cap.isOpened():  # Check if the external webcam is accessible
    print("External webcam not found. Falling back to the default camera.")
    cap = cv2.VideoCapture(0)  # Default camera

if not cap.isOpened():  # Check if the default camera is accessible
    print("No camera found. Exiting...")
    exit()  # Exit if no camera is accessible

# Full-screen display window
cv2.namedWindow("YOLO Detection", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("YOLO Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Screen resolution (replace with your actual screen resolution)
screen_width = 1920
screen_height = 1080

# Track the last state
last_state = "stopped"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform detection
    results = model(frame, verbose=False)  # Results object
    detections = results[0].boxes  # Access the boxes in the first result

    # Process detections
    filtered_targets = []
    for box in detections:
        try:
            # Extract coordinates and confidence
            xyxy = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls)
            confidence = float(box.conf)
            label = model.names[class_id]

            # Process only 'person' and 'dog' with confidence > 70%
            if (label == 'person' and confidence > 0.8) or (label == 'dog' and confidence > 0.8):
                center_x = (xyxy[0] + xyxy[2]) / 2
                filtered_targets.append({
                    'center_x': center_x,
                    'x_min': int(xyxy[0]),
                    'y_min': int(xyxy[1]),
                    'x_max': int(xyxy[2]),
                    'y_max': int(xyxy[3]),
                    'label': label
                })
        except (IndexError, AttributeError):
            continue

    # Process if there are any filtered targets
    if filtered_targets:
        screen_center_x = frame.shape[1] // 2
        closest_target = min(filtered_targets, key=lambda t: abs(t['center_x'] - screen_center_x))

        # Determine the current state based on thresholds
        if closest_target['center_x'] < LEFT_THRESHOLD * frame.shape[1]:  # Left 40%
            current_state = "left"
        elif closest_target['center_x'] > RIGHT_THRESHOLD * frame.shape[1]:  # Right 40%
            current_state = "right"
        else:
            current_state = "middle"

        # Send command only if the state changes
        if current_state != last_state:
            if current_state == "left":
                arduino.write(b'R')  # Send 'R' command for CCW
                print("Sending CCW command to Arduino")
            elif current_state == "right":
                arduino.write(b'L')  # Send 'L' command for CW
                print("Sending CW command to Arduino")
            elif current_state == "middle":
                arduino.write(b'S')  # Send 'S' command to Stop
                print("Motor idle in middle zone")

            # Update last state
            last_state = current_state

        # Draw bounding box and label for the closest target
        x_min, y_min, x_max, y_max, label = closest_target['x_min'], closest_target['y_min'], closest_target['x_max'], closest_target['y_max'], closest_target['label']
        color = (0, 255, 0) if label == 'person' else (255, 0, 0)  # Green for humans, Blue for dogs
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.circle(frame, (int(closest_target['center_x']), (y_min + y_max) // 2), 5, (0, 0, 255), -1)
    else:
        # No targets detected
        if last_state != "stopped":
            arduino.write(b'S')  # Send 'S' command to Stop
            print("No targets detected. Motor stopped.")
            last_state = "stopped"

    # Display the resized frame while maintaining aspect ratio
    original_height, original_width = frame.shape[:2]
    aspect_ratio = original_width / original_height

    # Calculate new dimensions while maintaining the aspect ratio
    if screen_width / aspect_ratio <= screen_height:
        new_width = screen_width
        new_height = int(screen_width / aspect_ratio)
    else:
        new_height = screen_height
        new_width = int(screen_height * aspect_ratio)

    # Resize the frame to the new dimensions
    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Add black borders to center the frame on the screen
    top_border = (screen_height - new_height) // 2
    bottom_border = screen_height - new_height - top_border
    left_border = (screen_width - new_width) // 2
    right_border = screen_width - new_width - left_border

    black_frame = cv2.copyMakeBorder(
        resized_frame,
        top=top_border,
        bottom=bottom_border,
        left=left_border,
        right=right_border,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0)  # Black color for borders
    )

    # Display the centered frame
    cv2.imshow("YOLO Detection", black_frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        arduino.write(b'S')  # Send 'S' command to Stop
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
arduino.close()
