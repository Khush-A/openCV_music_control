import cv2
import mediapipe as mp
import numpy as np
from math import hypot
import os
import pyautogui
import time

# grab frame from camera
cap = cv2.VideoCapture(0)

# set up hand tracking
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

volMin, volMax = 0, 100

last_action_time = 0
action_cooldown = 1.0

swipe_start_x = None
swipe_start_time = 0
gesture_active = False
swipe_threshold = 80
max_swipe_time = 0.7


def fingers_up(lmList):
    fingers = []

    # if thumb tip is right of thumb joint -> thumb is up
    # if thumb tip is left of thumb joint -> thumb is down

    if lmList[4][1] > lmList[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    # check other four fingers, up or down - (0,0) at top of the screen
    for tip, pip in zip(tips, pips):
        if lmList[tip][2] < lmList[pip][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return fingers

while True:
    # read frames
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # list of processed hands
    results = hands.process(imgRGB)

    # stores all landmarks in list
    lmList = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            # draws small circles for each landmark and connects them with lines
            # i.e. the hand skeleton
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)
        
    # using 21 landmarks
    if lmList != []:

        
        x1, y1 = lmList[4][1], lmList[4][2] # thumb tip
        x2, y2 = lmList[8][1], lmList[8][2] # index finger tip

        # calculate average x of the points between middle and index
        index_x = lmList[8][1]
        middle_x = lmList[12][1]
        x_avg = (index_x + middle_x) // 2

        fingers = fingers_up(lmList)
        now = time.time()

        volume_gesture = (fingers==[1, 1, 0, 0, 0])
        two_fingers_up = (fingers == [0, 1, 1, 0, 0])

        if volume_gesture:
            # draws points and lines
            cv2.circle(img, (x1, y1,), 4, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2,), 4, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            length = hypot(x2-x1, y2-y1)

            # map distance to the volume
            vol = np.interp(length,[15,220], [volMin, volMax])
            os.system(f"osascript -e 'set volume output volume {int(vol)}'")
            
            print(vol, length)

            gesture_active = False
            swipe_start_x = None
            swipe_start_time = 0

        elif two_fingers_up:
            if not gesture_active:
                # detected twp fingers up, start tracking movement
                gesture_active = True
                swipe_start_x = x_avg
                swipe_start_time = now
            else:
                delta_x = x_avg - swipe_start_x
                # swipe must finish quick enough and swipe must move far enough sideways
                if (now - swipe_start_time) < max_swipe_time and abs(delta_x) > swipe_threshold:
                    if now - last_action_time > action_cooldown:
                        if delta_x > 0:
                            print("SWIPE LEFT -> NEXT")
                            pyautogui.hotkey('command', 'left')
                        else:
                            print("SWIPE RIGHT -> NEXT")
                            pyautogui.hotkey('command', 'right')
                        
                        last_action_time = now
                    
                    # reset state
                    gesture_active = False
                    swipe_start_x = None
                    swipe_start_time = 0
        else:
            gesture_active = False
            swipe_start_x = None
            swipe_start_time = 0

    # show the image
    cv2.imshow('Image', img)

    # quit
    if cv2.waitKey(1) & 0xff==ord('q'):
        break
