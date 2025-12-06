
This project uses OpenCV, MediaPipe, and PyAutoGUI to control your Mac using hand gestures captured from your webcam.

It currently supports:
- Volume Control using a thumb–index pinch gesture
- Next / Previous Track using a two-finger swipe gesture

# Features
  1. Volume Control (Pinch Gesture)
    - Raise thumb + index finger only:
    - Move the fingers closer or farther apart to increase/decrease volume

  3. Swipe Gestures for Media Control
    - Raise index + middle fingers (peace sign):
    - Swipe right → Next track (⌘ + →)
    - Swipe left → Previous track (⌘ + ←)


# Requirements

Install dependencies:
- pip install opencv-python mediapipe numpy pyautogui

macOS also requires:
- Terminal under: System Settings → Privacy → Accessibility

Run the Project
- python main.py

Notes
- Make sure your music app is focused (Spotify / Apple Music / YouTube) when performing swipe gestures.
- Works on macOS (uses AppleScript instead of pycaw).
