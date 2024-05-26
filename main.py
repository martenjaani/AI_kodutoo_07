import tkinter as tk
from tkinter import Canvas
import random
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Setup camera capture
cap = cv2.VideoCapture(0)

# Create game environment
class Breakout:
    def __init__(self, master):
        self.master = master
        self.master.title("Breakout Game with Camera Feed")
        self.master.geometry("1600x400")  # Total window width increased for clear division

        self.canvas = Canvas(master, width=800, height=400, bg='black')  # Game canvas size
        self.canvas.pack(side=tk.LEFT)

        self.camera_canvas = Canvas(master, width=800, height=400, bg='grey')  # Camera feed canvas size
        self.camera_canvas.pack(side=tk.RIGHT)

        # Create paddle
        self.paddle = self.canvas.create_rectangle(0, 0, 100, 20, fill='blue')
        self.canvas.move(self.paddle, 350, 375)

        # Create ball
        self.ball = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.move(self.ball, 390, 360)

        self.ball_x_change = random.choice([-2.5, 2.5])
        self.ball_y_change = -2.5

        # Draw bricks
        self.bricks = []
        self.setup_bricks()

        # Update game
        self.update_game()

        # Update camera feed
        self.update_camera_feed()

    def setup_bricks(self):
        colors = ['green', 'yellow', 'orange', 'white']
        for i in range(4):
            for j in range(15):
                brick = self.canvas.create_rectangle(j * 53, i * 25, j * 53 + 50, i * 25 + 20, fill=colors[i], outline='black')
                self.bricks.append(brick)

    def update_game(self):
        self.move_ball()
        self.check_collisions()
        self.master.after(50, self.update_game)

    def move_ball(self):
        self.canvas.move(self.ball, self.ball_x_change, self.ball_y_change)
        pos = self.canvas.coords(self.ball)
        if pos[2] >= 800 or pos[0] <= 0:
            self.ball_x_change = -self.ball_x_change
        if pos[1] <= 0:
            self.ball_y_change = -self.ball_y_change
        if pos[3] >= 400:
            self.canvas.create_text(400, 200, text='Game Over', fill='red', font=('Helvetica', 30))
            self.ball_x_change = self.ball_y_change = 0

    def check_collisions(self):
        ball_pos = self.canvas.coords(self.ball)
        items = self.canvas.find_overlapping(*ball_pos)
        for item in items:
            if item in self.bricks:
                self.ball_y_change = -self.ball_y_change
                self.canvas.delete(item)
                self.bricks.remove(item)

    def update_camera_feed(self):
        success, image = cap.read()
        if success:
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    paddle_x = index_tip.x * 800  # Adjusted to map within the game canvas width
                    self.canvas.coords(self.paddle, paddle_x - 50, 375, paddle_x + 50, 395)

            image = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image=image)
            self.camera_canvas.create_image(0, 0, image=self.photo, anchor='nw')

        self.master.after(15, self.update_camera_feed)

if __name__ == "__main__":
    root = tk.Tk()
    app = Breakout(root)
    root.mainloop()
