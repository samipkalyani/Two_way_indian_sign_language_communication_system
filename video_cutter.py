import os
import shutil
import cv2
import mediapipe as mp
from datetime import datetime
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('./protected/test/word/test.mp4')
down = []
down_arr = []

flag = 0

fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_duration = frame_count / fps
print(total_duration)

with mp_hands.Hands(min_detection_confidence=0.75,min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            break
            # continue

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            if flag==1:
                if len(down_arr)>= 10:
                    down.append(sum(down_arr)/len(down_arr)) 
                flag=0
            # for hand_landmarks in results.multi_hand_landmarks:
            #     mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:  
            if flag==0:
                down_arr=[] 
                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                duration = frame_number / fps
                down_arr.append(duration)
                flag=1
            else:
                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                duration = frame_number / fps
                down_arr.append(duration)
            # cv2.imshow('MediaPipe Hands', image)
    # if cv2.waitKey(5) & 0xFF == 27:
    #   break
    if len(down_arr)>= 10:
        down.append(sum(down_arr)/len(down_arr)) 
cap.release()
print("down: ")
print(down)

for i in range(1, len(down)):
    os.mkdir("./protected/test"+str(i))
    os.mkdir("./protected/test"+str(i)+"/word"+str(i))
    os.system("ffmpeg -t "+str(down[i])+" -i ./protected/test/word/test.mp4 -ss "+str(down[i-1])+" ./protected/test/word"+str(i)+"/word"+str(i)+".mp4")
















