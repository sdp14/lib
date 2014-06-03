import time
import cv2
import numpy as np
from TramAction import TramAction
# E cv2 is a function that is part of cv (function that smart people wrote)
 

def morphOps(thresh):
    erodeElement = cv2.getStructuringElement(getattr(cv2, 'MORPH_RECT'), (4, 4))
    dilateElement = cv2.getStructuringElement(getattr(cv2, 'MORPH_RECT'), (8, 8))

    #res = cv2.morphologyEx(thresh, getattr(cv2, 'MORPH_ERODE'), erodeElement, iterations=1)

    erosion = cv2.erode(thresh,erodeElement,iterations = 5)
    dilation = cv2.dilate(erosion,dilateElement,iterations = 5)

    return dilation

    #cv2.imshow('res',dilation)


def trackbar():
   # global H_MIN, H_MAX, S_MIN, S_MAX, V_MIN, V_MAX

    cv2.namedWindow('TrackBarWindow')

    cv2.createTrackbar('H_MIN', 'TrackBarWindow', 0, 256, on_trackbar)
    cv2.createTrackbar('H_MAX', 'TrackBarWindow', 0, 256, on_trackbar)
    cv2.createTrackbar('S_MIN', 'TrackBarWindow', 0, 256, on_trackbar)
    cv2.createTrackbar('S_MAX', 'TrackBarWindow', 0, 256, on_trackbar)
    cv2.createTrackbar('V_MIN', 'TrackBarWindow', 0, 256, on_trackbar)
    cv2.createTrackbar('V_MAX', 'TrackBarWindow', 0, 256, on_trackbar)

#need function for createTrackbar to call, do not delete
#look at opencv docs to see why it is needed
def on_trackbar(args):
    pass

#mode tells wether the function is tracking or is in calibration mode
#mode = 0 is tracking mode = 1 is calibration
def start_video(mode):
    # create video capture
    H_MIN = 0
    H_MAX = 256
    S_MIN = 0
    S_MAX = 256
    V_MIN = 0
    V_MAX = 256

    position_array = {1:{"order":-1}, 2:{"order":-1}, 3:{"order":-1}}
    order = 0
    count = 0

    cap = cv2.VideoCapture(0)
#    if(~cap.isOpened()):
#        return False


    if(mode == 1):
    	trackbar()

    written = True

    while(1):

        # read the frames
        _,frame = cap.read()

        # smooth it
        frame = cv2.blur(frame,(3,3))



	if(mode == 1):
        	H_MIN = cv2.getTrackbarPos('H_MIN', 'TrackBarWindow')
        	H_MAX = cv2.getTrackbarPos('H_MAX', 'TrackBarWindow')
        	S_MIN = cv2.getTrackbarPos('S_MIN', 'TrackBarWindow')
        	S_MAX = cv2.getTrackbarPos('S_MAX', 'TrackBarWindow')
        	V_MIN = cv2.getTrackbarPos('V_MIN', 'TrackBarWindow')
        	V_MAX = cv2.getTrackbarPos('V_MAX', 'TrackBarWindow')



        # convert to hsv and find range of colors
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

        #if in calibration mode get filter details from trackbar
        if(mode == 1):
        	thresh = cv2.inRange(hsv,np.array((H_MIN, S_MIN, V_MIN)), np.array((H_MAX, S_MAX, V_MAX)))

        #if in tracking mode then the filter details have already been set
        elif(mode == 0):
        	thresh = cv2.inRange(hsv,np.array((0, 147, 22)), np.array((256, 256, 256)))
        #thresh2 = thresh.copy()
        # parameters of min and max values obtained using sliders
        thresh2 = morphOps(thresh)
        # find contours in the threshold image
        contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

        # finding contour with maximum area and store it as best_cnt
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                best_cnt = cnt

        if(max_area > 8000):
#            print max_area
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            #cx= x-ccordinate center point, cy= y-coordinate point
            cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])

            #print "The area is " + str(area)

            if(cx >= 0 and cx <=213):
#                print "Position 1 increased"
                if(not written):
                    TramAction.location = 1
                    written = True
#		return 1

            elif(cx >= 214 and cx <=426):
#                print "Position 2 increased"
                if(not written):
                    TramAction.location = 2
                    written = True
#                return 2

            elif(cx >= 427 and cx <=640):
#                print "Position 3 increased"
                if(not written):
                    TramAction.location = 3
                    written = True
#                return 3

            cv2.circle(frame,(cx,cy),5,255,-1)


        else:
            TramAction.location = 0
            written = False

        #morphOps(thresh2)
        # Show it, if key pressed is 'Esc', exit the loop
        cv2.imshow('frame',frame)
        cv2.imshow('thresh',thresh2)
        if cv2.waitKey(33)== 27:
            break


    # Clean up everything before leaving
    cv2.destroyAllWindows()
    cap.release()

class Tracking():

    def tracking(self):

        start_video(0)
        # E when changed to start_video(1) 
        # E calibrates the image detection system 
        # E this brings up the window containing sliders for each color detected by the webcam
#	    return start_video(mode)


