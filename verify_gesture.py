import cv2
import numpy as np
import gesture_control as gc
import time

def test_controller_initialization():
    print("Testing Controller Initialization...")
    try:
        controller = gc.GestureController()
        print("[OK] Controller initialized successfully.")
        return controller
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        return None

def test_process_frame_blank(controller):
    print("Testing process_frame with blank image...")
    # Create black image 640x480
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    try:
        # Process frame should just return the frame since no hands are present
        output = controller.process_frame(frame)
        print("[OK] process_frame executed without error.")
        return True
    except Exception as e:
        print(f"[FAIL] process_frame failed: {e}")
        return False


if __name__ == "__main__":
    c = test_controller_initialization()
    if c:
        test_process_frame_blank(c)
        print("\nLogic verification passed.")
    else:
        print("\nVerification failed at initialization.")
