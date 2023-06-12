import cv2
import numpy as np
from cv2 import VideoCapture
# from collections import deque

# define a video capture object
vid = cv2.VideoCapture(0)
count = 0
pts = []
pts2 = []
ptstracked = []
PreviousTracked = None

global Lower
global Upper
Lower = None
Upper = None


def distancepoints(point1, point2) : 
    difference = 0
    difference = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return difference

color = input('\nPlease select the colour of the object you want to track:\n 1. Black\n 2. Blue\n 3. Red\n 4. Green\n ===>Input: ')
color = int(color)

if color == 1 : #BLACK
    Lower = (0,0,0)
    Upper = (80, 255, 30)

elif color == 2 : #BLUE
    Lower = (80, 50, 70)
    Upper = (120, 255, 252)

elif color == 3 : #RED
    Lower = (0,100,50) #bruh
    Upper = (10,255,255)

elif color == 4 : #GREEN
    print('Green')
    Lower = (36, 50, 70)
    Upper = (89, 255, 255)

else : print('please enter the number corresponding to the color you wish to select')

print('============== *** Obtaining Input from video Feed *** =====================')
while(True):
    count+=1
    _, pic = vid.read()
    
    frame = pic
    # framesize = cv2.resize(frame, (600, 600),interpolation = cv2.INTER_LINEAR)
    frameblur = cv2.GaussianBlur(frame, (3,3),0)
    framehsv = cv2.cvtColor(frameblur, cv2.COLOR_BGR2HSV)

    #mask range
    # color_dict_HSV = {'black': [[180, 255, 30], [0, 0, 0]],
    #           'white': [[180, 18, 255], [0, 0, 231]],
    #           'red1': [[180, 255, 255], [159, 50, 70]],
    #           'red2': [[9, 255, 255], [0, 50, 70]],
    #           'green': [[89, 255, 255], [36, 50, 70]],
    #           'blue': [[128, 255, 255], [90, 50, 70]],
    #           'yellow': [[35, 255, 255], [25, 50, 70]],
    #           'purple': [[158, 255, 255], [129, 50, 70]],
    #           'orange': [[24, 255, 255], [10, 50, 70]],
    #           'gray': [[180, 18, 230], [0, 0, 40]]}

    
   
    
    mask = cv2.inRange(framehsv, Lower, Upper)
    maskop = cv2.morphologyEx(mask, cv2.MORPH_OPEN, (9,9))
    maskop = cv2.morphologyEx(maskop, cv2.MORPH_CLOSE, (9,9))
    # maskop = cv2.erode(mask, None, iterations=2)
    # maskop = cv2.dilate(maskop, None, iterations=2)
    _,thresh = cv2.threshold(maskop , 40, 255, 0)
    
    output = cv2.bitwise_and(frame, frame, mask=maskop)
    # output = thresh
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    if len(contours) != 0:
        cv2.drawContours(output, contours, -1, (0,0,128), 3)
        areas = [cv2.contourArea(c) for c in contours]
        # areas2 = [cv2.contourArea(c) for c in contours]
        
        max = 0
        max_index = np.argmax(areas)
        
        # if len(areas) > 1 : 
        for i in range(len(areas)) : 
            if (areas[i] > max) and (areas[i] != areas[max_index]) : 
                max = areas[i]
                max_index2 = i

        if (areas[max_index] > 5000) :
            cnt=contours[max_index]
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            # cv2.circle(frame, (int(x), int(y)), int(radius),(0, 0, 255), 2)
            # cv2.circle(output, (int(x), int(y)), int(radius),(0, 0, 255), 2)
            pts.append((int(x), int(y)))
        
        if len(areas)>2: 
            if(areas[max_index2] > 5000) :
                cnt2=contours[max_index2]
                ((x2, y2), radius2) = cv2.minEnclosingCircle(cnt2)
                # cv2.circle(frame, (int(x2), int(y2)), int(radius2),(0, 255, 0), 2)
                # cv2.circle(output, (int(x2), int(y2)), int(radius2),(0, 255, 0), 2)
                # print([areas[max_index], areas[max_index2]])
                pts2.append((int(x2), int(y2)))


    
    # print(count, 'pts',  pts)
    
    diffwLargest = 0
    diffwSecond = 0
    
    if len(pts) > 1 and len(pts2) >1 : 
        CurrentLargest = pts[-1]
        CurrentSecond = pts2[-1]
        if len(ptstracked) > 1: 
            PreviousTracked = ptstracked[-1]
        
        if PreviousTracked is not None : 
            diffwLargest = distancepoints(CurrentLargest, PreviousTracked)
            diffwSecond = distancepoints(CurrentSecond, PreviousTracked)
        
        
        if (diffwLargest < 500) : 
            print('Current largest')
            ptstracked.append(CurrentLargest)
            cv2.circle(frame, (CurrentLargest[0], CurrentLargest[1]), int(radius),(0, 0, 255), 2)
            cv2.circle(frame, (CurrentLargest[0], CurrentLargest[1]), int(radius),(0, 0, 255), 2)
            
        elif (diffwLargest > 500) and (diffwSecond < 500) :
            print('Second Largest')
            ptstracked.append(CurrentSecond)
            cv2.circle(frame, (CurrentSecond[0], CurrentSecond[1]), int(radius2),(0, 255, 0), 2)
            cv2.circle(output, (CurrentSecond[0], CurrentSecond[1]), int(radius2),(0, 255, 0), 2)
            # print('Distance too large: misdetection suspected')
        
        else : print('object gayab ho gya')   
    
    
    pts = pts[-20:]
    pts2 = pts2[-20:]
    ptstracked = ptstracked[-20:]
    
    ptstrackedNP = np.array(ptstracked)
    cv2.polylines(frame,[ptstrackedNP],False,(0,0,255), 3)
    
    # print('pts: ', pts)
    cv2.imshow('og pic', pic)
    cv2.imshow('color mask', mask)
    cv2.imshow('contour output', output)
    cv2.imshow('final tracked frame', frame)
    
    # cv2.imshow('mask - opening', mask)
    # cv2.imshow('output', output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()