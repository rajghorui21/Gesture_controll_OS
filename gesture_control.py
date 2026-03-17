import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# --- Configuration ---
# Screen Resolution
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Active Area Box (Normalized coordinates 0.0 to 1.0)
# This box restricts the mouse movement to a smaller region in the camera view
BOX_X_START, BOX_X_END = 0.1, 0.9
BOX_Y_START, BOX_Y_END = 0.1, 0.9

# Dynamic Smoothing (Speed-aware)
SMOOTHING_MIN = 0.05  # Steady: lowers jitter
SMOOTHING_MAX = 0.6   # Moving: reduces lag
SPEED_THRESHOLD = 80  # Speed in pixels to hit max responsiveness factor

# Thresholds
CLICK_DISTANCE_THRESHOLD = 30  # pixels
SCROLL_THRESHOLD = 15          # pixels
VOLUME_THRESHOLD = 15          # pixels

# PyAutoGUI Safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001  # Reduce delay for smoother movement

class GestureController:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Screen dimensions
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Previous Coordinates for smoothing
        self.prev_x, self.prev_y = 0, 0
        
        # State Management
        self.is_clicked = False
        self.fist_enabled = False
        self.fist_start_y = 0
        self.prev_fist_y = 0
        
        # Swipe tracking
        self.pos_history = []
        self.history_size = 5
        self.swipe_cooldown = 0
        
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def is_fist(self, landmarks, frame_h):
        """Detect if the hand is a fist (four fingers folded)."""
        # Landmark indices:
        # Index: Tip 8, Joint 6
        # Middle: Tip 12, Joint 10
        # Ring: Tip 16, Joint 14
        # Pinky: Tip 20, Joint 18
        
        # MediaPipe coords are normalized [0,1]. Top is 0, bottom is 1.
        # If tip Y > joint Y, it means the finger is folded (lower on screen).
        fingers_folded = []
        
        # Index
        fingers_folded.append(landmarks[8].y > landmarks[6].y)
        # Middle
        fingers_folded.append(landmarks[12].y > landmarks[10].y)
        # Ring
        fingers_folded.append(landmarks[16].y > landmarks[14].y)
        # Pinky
        fingers_folded.append(landmarks[20].y > landmarks[18].y)
        
        # All 4 fingers folded
        return all(fingers_folded)

    def process_frame(self, frame):
        h, w, c = frame.shape
        # Flip frame horizontally for natural mirror view
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        # Draw Active Box
        start_pt = (int(BOX_X_START * w), int(BOX_Y_START * h))
        end_pt = (int(BOX_X_END * w), int(BOX_Y_END * h))
        cv2.rectangle(frame, start_pt, end_pt, (255, 0, 0), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark

                # 1. Get Core Landmarks (Pixel coords)
                # Index Tip (8), Thumb Tip (4)
                index_pos = (int(landmarks[8].x * w), int(landmarks[8].y * h))
                thumb_pos = (int(landmarks[4].x * w), int(landmarks[4].y * h))
                wrist_pos = (int(landmarks[0].x * w), int(landmarks[0].y * h))

                # 2. Check for Fist (Volume Control)
                fist_detected = self.is_fist(landmarks, h)
                cv2.putText(frame, f"Fist: {fist_detected}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if fist_detected:
                    # In Fist Mode, use wrist or fist center for tracking height
                    current_fist_y = wrist_pos[1]
                    cv2.circle(frame, wrist_pos, 10, (0, 0, 255), -1)

                    if not self.fist_enabled:
                        self.fist_enabled = True
                        self.prev_fist_y = current_fist_y
                    else:
                        diff = self.prev_fist_y - current_fist_y  # -ive means moving down, +ive means moving up
                        if abs(diff) > VOLUME_THRESHOLD:
                            if diff > 0:
                                pyautogui.press('volumeup')
                                cv2.putText(frame, "Volume UP", (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            else:
                                pyautogui.press('volumedown')
                                cv2.putText(frame, "Volume DOWN", (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            self.prev_fist_y = current_fist_y
                    
                    # Skip mouse movement in Fist Mode
                    return frame

                else:
                    self.fist_enabled = False

                # 3. Swipe Detection (Tab Switching)
                if self.swipe_cooldown > 0:
                    self.swipe_cooldown -= 1
                else:
                    self.pos_history.append(wrist_pos[0])  # Track X of wrist
                    if len(self.pos_history) > self.history_size:
                        self.pos_history.pop(0)
                        
                        # Calculate movement
                        dx = self.pos_history[-1] - self.pos_history[0]
                        if abs(dx) > 100:  # Threshold for swipe
                            if dx > 0:
                                # Swipe Right -> Switch Tab Next
                                pyautogui.hotkey('ctrl', 'tab')
                                cv2.putText(frame, "Swipe Right -> Tab Next", (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            else:
                                # Swipe Left -> Switch Tab Previous
                                pyautogui.hotkey('ctrl', 'shift', 'tab')
                                cv2.putText(frame, "Swipe Left -> Tab Prev", (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            self.swipe_cooldown = 15  # frames cooldown
                            self.pos_history = []
                            return frame

                # 4. Mouse Movement (Index Finger)
                # Map from camera active box to full screen
                # Camera is flipped, so we use coordinate scaling
                norm_x = landmarks[8].x
                norm_y = landmarks[8].y

                # Limit to active box
                if BOX_X_START <= norm_x <= BOX_X_END and BOX_Y_START <= norm_y <= BOX_Y_END:
                    # Scale
                    scaled_x = np.interp(norm_x, [BOX_X_START, BOX_X_END], [0, self.screen_width])
                    scaled_y = np.interp(norm_y, [BOX_Y_START, BOX_Y_END], [0, self.screen_height])

                    # Smooth
                    # Dynamic Smoothing calculation
                    speed = np.sqrt((scaled_x - self.prev_x)**2 + (scaled_y - self.prev_y)**2)
                    dyn_smoothing = np.interp(speed, [0, SPEED_THRESHOLD], [SMOOTHING_MIN, SMOOTHING_MAX])

                    curr_x = self.prev_x + (scaled_x - self.prev_x) * dyn_smoothing
                    curr_y = self.prev_y + (scaled_y - self.prev_y) * dyn_smoothing

                    # Move Mouse
                    pyautogui.moveTo(int(curr_x), int(curr_y))
                    
                    self.prev_x, self.prev_y = curr_x, curr_y
                    
                    # Draw cursor on frame for debug
                    cv2.circle(frame, index_pos, 10, (0, 255, 0), -1)

                # 5. Pinch to Click
                distance = self.calculate_distance(index_pos, thumb_pos)
                cv2.putText(frame, f"Dist: {int(distance)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                if distance < CLICK_DISTANCE_THRESHOLD:
                    if not self.is_clicked:
                        pyautogui.click()
                        self.is_clicked = True
                        cv2.putText(frame, "CLICK!", (w // 2, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                else:
                    self.is_clicked = False

        return frame

def main():
    cap = cv2.VideoCapture(0)
    controller = GestureController()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Process frame
        output_frame = controller.process_frame(frame)

        # Display output
        cv2.imshow('Gesture Control Interface', output_frame)

        # Break loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
