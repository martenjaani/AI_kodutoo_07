import tkinter as tk
from tkinter import Canvas
import random
import cv2
from PIL import Image, ImageTk
import mediapipe as mp

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Setup camera capture
cap = cv2.VideoCapture(0)

class Breakout:
    def __init__(self, master):
        self.master = master
        self.master.title("Breakout Game with Camera Feed")
        self.master.geometry("1600x400")

        self.canvas = Canvas(master, width=800, height=400, bg='black')
        self.canvas.pack(side=tk.LEFT)
        self.camera_canvas = Canvas(master, width=800, height=400, bg='grey')
        self.camera_canvas.pack(side=tk.RIGHT)

        self.reset_gesture_frames = 0
        self.exit_gesture_frames = 0
        self.required_gesture_frames = 10  # Number of frames to recognize gesture before acting

        self.setup_game()
        self.update_game()
        self.update_camera_feed()

    def setup_game(self):
        self.game_over = False
        self.won = False
        self.canvas.delete("all")
        self.reset_gesture_frames = 0
        self.exit_gesture_frames = 0

        # Create paddle
        self.paddle = self.canvas.create_rectangle(350, 375, 450, 395, fill='blue')

        # Create ball
        self.ball = self.canvas.create_oval(390, 360, 410, 380, fill='red')
        self.ball_x_change = random.choice([-2.5, 2.5])
        self.ball_y_change = -5

        # Draw bricks
        self.bricks = []
        colors = ['green', 'yellow', 'orange', 'white']
        for i in range(4):
            for j in range(15):
                brick = self.canvas.create_rectangle(j * 53, i * 25, j * 53 + 50, i * 25 + 20, fill=colors[i], outline='black')
                self.bricks.append(brick)

    def update_game(self):
        if not self.game_over and not self.won:
            self.move_ball()
            self.check_collisions()
            self.check_paddle_collision()
        self.master.after(50, self.update_game)

    def move_ball(self):
        self.canvas.move(self.ball, self.ball_x_change, self.ball_y_change)
        pos = self.canvas.coords(self.ball)
        if pos[2] >= 800 or pos[0] <= 0:
            self.ball_x_change = -self.ball_x_change
        if pos[1] <= 0:
            self.ball_y_change = -self.ball_y_change
        if pos[3] >= 400 and not self.won:
            self.canvas.create_text(400, 200, text='Game Over', fill='red', font=('Helvetica', 30))
            self.ball_x_change = self.ball_y_change = 0
            self.game_over = True

    def check_collisions(self):
        ball_pos = self.canvas.coords(self.ball)
        items = self.canvas.find_overlapping(*ball_pos)
        for item in items:
            if item in self.bricks:
                self.ball_y_change = -self.ball_y_change
                self.canvas.delete(item)
                self.bricks.remove(item)
        if not self.bricks and not self.game_over:
            self.won = True
            self.canvas.create_text(400, 200, text='You Won!', fill='green', font=('Helvetica', 30))
            self.ball_x_change = self.ball_y_change = 0

    def check_paddle_collision(self):
        ball_pos = self.canvas.coords(self.ball)
        paddle_pos = self.canvas.coords(self.paddle)
        if (ball_pos[2] >= paddle_pos[0] and ball_pos[0] <= paddle_pos[2] and
                ball_pos[3] >= paddle_pos[1] and ball_pos[1] <= paddle_pos[3]):
            self.ball_y_change = -abs(self.ball_y_change)

    def fingers_up(self, hand_landmarks):
        finger_tips = [
            mp_hands.HandLandmark.THUMB_TIP,
            mp_hands.HandLandmark.INDEX_FINGER_TIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            mp_hands.HandLandmark.RING_FINGER_TIP,
            mp_hands.HandLandmark.PINKY_TIP
        ]
        count = 0
        for tip in finger_tips:
            tip_index = tip
            pip_index = tip - 2 if tip != mp_hands.HandLandmark.THUMB_TIP else tip - 1
            if hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[pip_index].y:
                count += 1
        return count

    def update_camera_feed(self):
        success, image = cap.read()
        if success:
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    paddle_x = index_tip.x * 800  # Adjust to the game canvas width
                    paddle_x = max(50, min(paddle_x, 750))
                    self.canvas.coords(self.paddle, paddle_x - 50, 375, paddle_x + 50, 395)

                    fingers_counted = self.fingers_up(hand_landmarks)
                    if self.game_over or self.won:
                        if fingers_counted == 2:
                            if self.reset_gesture_frames >= self.required_gesture_frames:
                                self.setup_game()  # Restart if two fingers are consistently shown
                            else:
                                self.reset_gesture_frames += 1
                        elif fingers_counted == 5:
                            if self.exit_gesture_frames >= self.required_gesture_frames:
                                self.master.quit()  # Exit if five fingers are consistently shown
                            else:
                                self.exit_gesture_frames += 1
                    else:
                        self.reset_gesture_frames = 0
                        self.exit_gesture_frames = 0

            # Display the camera feed
            image_pil = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image=image_pil)
            self.camera_canvas.image = photo
            self.camera_canvas.create_image(0, 0, image=photo, anchor='nw')

        self.master.after(15, self.update_camera_feed)

if __name__ == "__main__":
    root = tk.Tk()
    app = Breakout(root)
    root.mainloop()
