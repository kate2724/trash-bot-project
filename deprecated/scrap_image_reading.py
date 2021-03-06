import cv2
import numpy as np

cam = cv2.VideoCapture(0)
ret, frame = cam.read()
objectFound = False
objectGrabbable = False

if frame is not None:
    while True:
        ret, frame = cam.read()
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        cv2.imshow("hsv", hsv)

        blueFiltered = cv2.inRange(hsv, (100, 100, 70), (150, 255, 230))
        redFiltered = cv2.inRange(hsv, (150, 70, 115), (190, 210, 220))
        cv2.imshow("final", blueFiltered)
        # cv2.imshow("final", redFilteredq)

        contrsBlue, hierBlue = cv2.findContours(blueFiltered, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contrsRed, hierRed = cv2.findContours(redFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(frame, contrs, -1, (0, 255, 0), 3)

        xMin = 100
        yMin = 320
        xMax = 520
        yMax = 479
        grabbingBox = cv2.rectangle(frame, (xMin, yMin), (xMax, yMax), (255, 255, 255), 2)

        if len(contrsBlue) > 0:
            cBlue = max(contrsBlue, key=cv2.contourArea)
            xBlue, yBlue, wBlue, hBlue = cv2.boundingRect(cBlue)
            # actual coordinates are (x,y),(x+w,y), (x,y+h), (x+w,y+h)
            # robot turns until coordinates are centered
            # robot forward until area of coordinates passes certain threshold (means the robot is close enough)
            # robot grabs object
            # robot turns until it sees dumpster flag
            # same process as before, until it reaches dumpster

            # draw the biggest contour (c) in green
            if cv2.contourArea(cBlue) > 1250:
                blueRectangle = cv2.rectangle(frame, (xBlue, yBlue), (xBlue + wBlue, yBlue + hBlue), (0, 255, 0), 2)
                # print("blue coordinates: ", xBlue, yBlue, wBlue, hBlue)
                objectFound = True
                if (xBlue > xMin and xBlue < xMax and yBlue > yMin and yBlue < yMax):
                    print("within range")
                    objectGrabbable = True
                else:
                    objectGrabbable = False
            else:
                objectFound = False

        if len(contrsRed) > 0:
            cRed = max(contrsRed, key=cv2.contourArea)
            xRed, yRed, wRed, hRed = cv2.boundingRect(cRed)
            # draw the biggest contour (c) in blue
            if cv2.contourArea(cRed) > 1000:
                redRectangle = cv2.rectangle(frame, (xRed, yRed), (xRed + wRed, yRed + hRed), (255, 0, 0), 2)
                print("red coordinates: ", xRed, yRed, wRed, hRed)
                objectFound = True
            else:
                objectFound = False
        cv2.imshow('Contours', frame)
        # print("object Found: ", objectFound)
        ch = chr(0xFF & cv2.waitKey(5))
        if ch == 'q':
            break

cv2.waitKey(0)
cv2.destroyAllWindows()
