import mediapipe as mp
import cv2
import time
import math
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes  import cast, POINTER

x1=y1=x2=y2 = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

mp_drawing = mp.solutions.drawing_utils  #render all the different landmarks on the hand
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0) #getting our webcam feed

with mp_hands.Hands(min_detection_confidence=0.8,min_tracking_confidence=0.5, max_num_hands = 2) as hands:
  while cap.isOpened():  #while connected to webcam
    ret, frame = cap.read() #read each frame from webcam; frame = image from webcam; ret = return value

    #BGR 2 RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #flip on horizontal
    image =cv2.flip(image, 1)

    #set flag
    image.flags.writeable = False

    #Detection
    results = hands.process(image)

    #Set flag as true(now we can draw on this image)
    image.flags.writeable = True

    #RGB 2 BGR
    image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)

    #allows us to see our detections
    # print(results)
    frame_height, frame_width, _ = image.shape
    #rendering results
    if results.multi_hand_landmarks:
      for num,hand in enumerate(results.multi_hand_landmarks):
        mp_drawing.draw_landmarks(image,hand,mp_hands.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0,0,255),thickness =2,circle_radius = 4),  #circle landmarks BGR
                                  mp_drawing.DrawingSpec(color=(0,255,0),thickness=2,circle_radius=2),    #line BGR
        )
        landmarks = hand.landmark
        for id, landmark in enumerate ( landmarks ):

            # finding x,y points of index and thumb
            x = int ( landmark.x * frame_width )
            y = int ( landmark.y * frame_height )
            if id == 8:
                cv2.circle ( image, (x, y), 10, (255, 0, 255), 3, cv2.FILLED )
                x1 = x
                y1 = y
            if id == 4:
                cv2.circle ( image, (x, y), 10, (255, 0, 255), 3, cv2.FILLED )
                x2 = x
                y2 = y

      cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
      cv2.circle ( image, (cx, cy), 15, (255, 0, 255), cv2.FILLED )
      cv2.line ( image, (x1, y1), (x2, y2), (0, 255, 0), 3 )
      dist = math.hypot ( x2 - x1, y2 - y1 )
      # print ( dist )

      #Hand range = 240 to 40
      #Vol range = -65 to 0
      vol = np.interp(dist,[40,240],[minVol,maxVol])
      # print(vol)
      volume.SetMasterVolumeLevel ( vol, None )

      if dist<50:
          cv2.circle ( image, (cx, cy), 15, (0, 255, 0), cv2.FILLED )

    cv2.imshow("Hand Tracking", image) #render that image to the screen

    #to closedown the window by either hitting q or closing window
    if cv2.waitKey(10) & 0xFF == ord('q'):
      break

cap.release()
cv2.destroyAllWindows()
