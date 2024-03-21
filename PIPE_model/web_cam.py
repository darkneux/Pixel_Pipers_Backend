import cv2
from ultralytics import YOLO

# Replace "0" with the correct webcam ID if needed
cap = cv2.VideoCapture("/dev/v4l/by-path/pci-0000:00:14.0-usb-0:2:1.0-video-index0")

# Check if webcam is opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")
    exit()

model = YOLO("best.pt")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error reading frame from video stream or file")
        break

    results = model.predict(frame,conf=0.7, show=True)
    # print(results)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()
