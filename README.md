# Gesture-Controlled OS Interface

A Python application that uses your webcam to track hand landmarks in real-time and map specific gestures to actual operating system commands like mouse movement, clicking, volume control, and tab switching.

---

## 🛠️ Prerequisites

Make sure you have the required Python libraries installed:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

---

## 🚀 How to Run

Run the main script from your terminal:

```bash
python gesture_control.py
```

> [!IMPORTANT]
> **Safety Fail-Safe**: If you lose control of your mouse cursor at any time, quickly move your physical mouse to **any corner of your screen**. This triggers PyAutoGUI's fail-safe and aborts the script execution.

---

## 🖐️ Gestures Manual

The application draws an **Active Box** (blue rectangle) on the camera feed. To move the mouse, your hand must be tracked *inside* this box. This scales small hand movements to your full screen.

### 1. 🖱️ Mouse Cursor
-   **Movement**: Move your **Index Finger Tip** inside the blue rectangle. The mouse cursor will glide with smoothing.
-   **Click**: Bring your **Index Finger Tip** and **Thumb Tip** together (a "Pinch"). A short distance between them triggers a left-click.

### 2. 🔊 Volume Control (Fist)
-   **Gesture**: Fold inside all four fingers (Index, Middle, Ring, Pinky) into a **Fist**.
-   **Action**: 
    -   Move your fist **Up** to increase volume.
    -   Move your fist **Down** to decrease volume.
-   *Mouse movement is temporarily paused in Fist mode for safety.*

### 3. 🌐 Tab Switching (Swipe)
-   **Gesture**: Move your hand rapidly sideways (rapid change in X position).
-   **Action**:
    -   **Swipe Right**: Switches to the **Next Tab** (`Ctrl + Tab`).
    -   **Swipe Left**: Switches to the **Previous Tab** (`Ctrl + Shift + Tab`).

---

## ⚙️ Customization

You can adjust thresholds at the top of `gesture_control.py`:
-   `CLICK_DISTANCE_THRESHOLD`: Adjust pinch sensitivity.
-   `SMOOTHING`: Higher is smoother but has lag; lower is responsive but jittery.
-   `BOX_X_START/END`: Resize the Active Box area.

