import cv2
import numpy as np
import pyautogui
import mediapipe as mp

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Start capturing video
cap = cv2.VideoCapture(0)

screen_width, screen_height = pyautogui.size()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for natural (selfie-view) visualization
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the coordinates of the tip of the index finger
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Convert the normalized coordinates to screen coordinates
            x = int(index_finger_tip.x * frame_width)
            y = int(index_finger_tip.y * frame_height)

            # Convert to screen coordinates
            screen_x = int((x / frame_width) * screen_width)
            screen_y = int((y / frame_height) * screen_height)

            # Move the mouse to the calculated screen coordinates
            pyautogui.moveTo(screen_x, screen_y)

    # Display the frame
    cv2.imshow('Hand Tracking', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
hands.close()
