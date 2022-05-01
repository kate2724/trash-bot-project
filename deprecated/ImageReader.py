"""This file blah blah  blah blah
blah
By Katelyn Breen and Seth Wiseheart, 2022
"""
#!/usr/bin/env python


import numpy as np
import cv2

showBackProj = False
showHistMask = False
frame = None
histBlue = None
histRed = None

cam = cv2.VideoCapture(0)
ret, frame = cam.read()

if frame is not None:
    (hgt, wid, dep) = frame.shape
    # frame = cv2.resize(frame, dsize = (0, 0), fx = 0.5, fy = 0.5)
    # frame = getNextFrame(cam)
    cv2.namedWindow('ball detection')
    # cv2.namedWindow('hist')
    # cv2.moveWindow('hist', 700, 100)  # Move to reduce overlap

    # Initialize the track window to be the whole frame
    track_windowBlue = (0, 0, wid, hgt)
    track_windowRed = (0, 0, wid, hgt)

    # Initialize the histogram from the stored image

    # Here I am faking a stored image with just a couple of blue colors in an array
    # you would want to read the image in from the file instead
    histImageBlue = np.array([[[110, 70, 50]],
                              [[111, 128, 128]],
                              [[115, 100, 100]],
                              [[117, 64, 50]],
                              [[117, 200, 200]],
                              [[118, 76, 100]],
                              [[120, 101, 210]],
                              [[121, 85, 70]],
                              [[125, 129, 199]],
                              [[128, 81, 78]],
                              [[130, 183, 111]]], np.uint8)

    histImageRed = np.array([[[50, 70, 110]],
                              [[128, 128, 200]],
                              [[100, 100, 130]],
                              [[50, 64, 117]],
                              [[200, 200, 250]],
                              [[100, 76, 118]],
                              [[210, 101, 120]],
                              [[70, 85, 121]],
                              [[199, 129, 210]],
                              [[78, 81, 128]],
                              [[111, 120, 200]]], np.uint8)

    maskedHistImBlue = cv2.inRange(histImageBlue, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    histBlue = cv2.calcHist([histImageBlue], [0], maskedHistImBlue, [16], [0, 180])
    cv2.normalize(histBlue, histBlue, 0, 255, cv2.NORM_MINMAX)
    histBlue = histBlue.reshape(-1)

    maskedHistImRed = cv2.inRange(histImageRed, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    histRed = cv2.calcHist([histImageRed], [0], maskedHistImRed, [16], [0, 180])
    cv2.normalize(histRed, histRed, 0, 255, cv2.NORM_MINMAX)
    histRed = histRed.reshape(-1)
    # show_hist(hist)

    # start processing frames
    while True:
        ret, frame = cam.read()
        vis = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # convert to HSV
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)),
                           np.array((180., 255., 255.)))  # eliminate low and high saturation and value values


        # The next line shows which pixels are being used to make the histogram.
        # it sets to black all the ones that are masked away for being too over or under-saturated
        if showHistMask:
            vis[mask == 0] = 0

        probBlue = cv2.calcBackProject([hsv], [0], histBlue, [0, 180], 1)
        probBlue &= mask
        term_critBlue = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        track_boxBlue, track_windowBlue = cv2.CamShift(probBlue, track_windowBlue, term_critBlue)

        probRed = cv2.calcBackProject([hsv], [0], histRed, [0, 180], 1)
        probRed &= mask
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        track_boxRed, track_windowRed = cv2.CamShift(probRed, track_windowRed, term_crit)

        if showBackProj:
            vis[:] = probBlue[..., np.newaxis]
            vis[:] = probRed[..., np.newaxis]
        try:
            cv2.ellipse(vis, track_boxBlue, (255, 0, 0), 2)
            cv2.ellipse(vis, track_boxRed, (0, 0, 255), 2)
        except:
            print("Track box:", track_boxBlue)
            print("Track box:", track_boxRed)

        cv2.imshow('find blue', vis)

        ch = chr(0xFF & cv2.waitKey(5))
        if ch == 'q':
            break
        elif ch == 'b':
            showBackProj = not showBackProj
        elif ch == 'v':
            showHistMask = not showHistMask

cv2.destroyAllWindows()


