import cv2
import mediapipe as mp
import pyautogui
import numpy as np

print("Imports successful!")
print(f"OpenCV version: {cv2.__version__}")
print(f"MediaPipe version: {mp.__version__}")
print(f"NumPy version: {np.__version__}")

# Try to open webcam briefly
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("Webcam opened successfully!")
    cap.release()
else:
    print("Could not open webcam.")
print("PyAutoGUI works if we get here.")
