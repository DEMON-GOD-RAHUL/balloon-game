# Import
import pygame
import numpy as np
import random
import cv2
from cvzone.HandTrackingModule import HandDetector
import time

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BALLOON_COLORS = [
    '/Users/demongod/Documents/baloon/Red.png',
    '/Users/demongod/Documents/baloon/Pink.png',
    '/Users/demongod/Documents/baloon/Blue.png',
    '/Users/demongod/Documents/baloon/Green.png' 
]
FONT_PATH = '/Users/demongod/Documents/baloon/Marcellus-Regular.ttf'
SOUND_POP_PATH = '/Users/demongod/Documents/baloon/pop.mp3'
VIDEO_PATH = '/Users/demongod/Documents/baloon/video.mp4'  # Replace with the path to your video file

# Initialize
pygame.init()

# Create Window/Display
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balloon Pop")

# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, SCREEN_WIDTH)  # width
cap.set(4, SCREEN_HEIGHT)  # height

# Video
video_cap = cv2.VideoCapture(VIDEO_PATH)

# Images
balloon_colors = [pygame.image.load(color).convert_alpha() for color in BALLOON_COLORS]
rectBalloon = balloon_colors[0].get_rect()

# Functions
def reset_balloon():
    rectBalloon.x = random.randint(100, SCREEN_WIDTH - 100)
    rectBalloon.y = SCREEN_HEIGHT + 50

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(FONT_PATH, size)
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))

reset_balloon()  # Initial placement of the balloon

# Variables
speed = 5
score = 0
level = 1
startTime = time.time()
totalTime = 60


pop_sound = pygame.mixer.Sound(SOUND_POP_PATH)
color_index = 0  # Index to keep track of the current balloon color

# Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Main loop
while True:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Apply Logic
    time_remaining = int(totalTime - (time.time() - startTime))
    if time_remaining < 0:
        window.fill((0,0,0))

     # OpenCV - Display Video
        success_video, frame_video = video_cap.read()
        frame_video = frame_video.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
        cv2.imshow(frame_video)
        if not success_video:
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rewind the video when it ends

        frame_video = cv2.cvtColor(frame_video, cv2.COLOR_BGR2RGB)
        frame_video = np.rot90(frame_video)
        frame_video = pygame.surfarray.make_surface(frame_video).convert()
        frame_video = pygame.transform.flip(frame_video, True, False)
        window.blit(frame_video, (0,0))
        draw_text(f'Your Score: {score}', 50, (50, 50, 255), 450, 350)
        draw_text('Time UP', 50, (50, 50, 255), 530, 275)
        draw_text('Congratulations!', 50, (255, 0, 0), 450, 420)
    
    else:
        # OpenCV
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        rectBalloon.y -= speed  # Move the balloon up
        # Check if balloon has reached the top without popping
        if rectBalloon.y < 0:
            reset_balloon()
            speed += 0.5
            color_index = random.randint(0, len(balloon_colors) - 1)  # Cycle through colors

        if hands:
            hand = hands[0]
            x, y = hand['lmList'][8][0:2]
            if rectBalloon.collidepoint(x, y):
                reset_balloon()
                color_index = (color_index + 1) % len(balloon_colors)
                score += 10
                speed += 0.5
                pop_sound.play()

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))

        # Draw balloon with the current color
        window.blit(balloon_colors[color_index], rectBalloon)

        draw_text(f'Score: {score} | Level: {level}', 50, (50, 50, 255), 35, 35)
        draw_text(f'Time: {time_remaining}', 50, (50, 50, 255), 1000, 35)

        # Increase level every 100 points
        if score >= level * 100:
            level += 1
            speed += 0.5
            totalTime += 10  # Add more time for each new level

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
