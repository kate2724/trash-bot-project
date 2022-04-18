import cv2
import numpy as np
frame = None
cam = cv2.VideoCapture(0)
ret, frame = cam.read()
objectFound = False

if frame is not None:
    while True:
        ret, frame = cam.read()
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        # cv2.imshow("hue?", img2)
        # img3= cv2.inRange(img2, (100,50,40), (255,100,100))
        blueFiltered = cv2.inRange(hsv, (100, 100, 40), (150, 240, 230))

        redFiltered = cv2.inRange(hsv, (50, 40, 150), (120, 150, 255))
        # cv2.imshow("final", redFiltered)

        contrs, hier = cv2.findContours(blueFiltered, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        # contrs, hier = cv2.findContours(redFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(frame, contrs, -1, (0, 255, 0), 3)

        if(contrs is not None):
            c = max(contrs, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

            # draw the biggest contour (c) in green
            if(cv2.contourArea(c)>1250):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                objectFound=True
            else:
                objectFound=False
            cv2.imshow('Contours', frame)
        print("object Found: ", objectFound)
        ch = chr(0xFF & cv2.waitKey(5))
        if ch == 'q':
            break

cv2.waitKey(0)
cv2.destroyAllWindows()