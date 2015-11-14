import cv2
import numpy as np
import time
import math


#This Function looks at each frame from the camera and detects a bullseye pattern(Nested Circles) of a certain predefined ratio
def nothing(x):
    pass

def search_frame(img):


    #Apply a blur and convert to grayscale
    #img2 = cv2.medianBlur(img,3)
    img2 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Perhaps search for color image first in event of nightime landing

    #Apply adaptive thresholding
    avg,null,null,null = cv2.mean(img2)
    #th = cv2.getTrackbarPos('Thresh','Threshold')
    th = int(avg)
    ret,img2 = cv2.threshold(img2,th,255,cv2.THRESH_BINARY)
    #cv2.imshow('Threshold',img2)

    #Dilate the image to make detection easier
    kernel = np.ones((5,5),np.uint8)
    img2 = cv2.morphologyEx(img2,cv2.MORPH_CLOSE, kernel, borderType=cv2.BORDER_CONSTANT)

    #Edge detection
    low = cv2.getTrackbarPos('min Thresh','edges')
    hi = cv2.getTrackbarPos('max Thresh','edges')
    edges = cv2.Canny(img2,100,200,2)
    #cv2.imshow('edges',edges)
    if edges is not None:
        
        contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #find circles
        circles = np.empty((len(contours)),object)
        circlesCnt = 0
        for i in xrange(0,len(contours)):
            contour = contours[i]
            if(len(contour) > 4):
                ellipse = cv2.fitEllipse(contour)
                
                if checkEcc(ellipse,.6):
                    circles[circlesCnt] = ellipse
                    #cv2.ellipse(img,ellipse,(255,0,0),2)
                    circlesCnt += 1
            
        if circlesCnt > 0:
            #look for nested circles
            circles = np.resize(circles,circlesCnt)
            nestedCirc = detNested(circles) 
        


            if len(nestedCirc) > (10):
                #check if they have a common center
                finTarget, center = findCommonCent(nestedCirc)
                if finTarget is not None:
                    for i in range(0,len(finTarget)):
                        cv2.ellipse(img,finTarget[i],(0,255,0),2)

                    #find ratio between rings
                    ratios = tagAspectRatio(finTarget)

                    if ratios is not None:
                        distance = CalcDistanceTarget(finTarget,ratios)
                        if distance != -1:
                            cv2.putText(img,'Distance: ' +str(distance)+' Meters',(20,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

    #function to detect ditance between center of 2 ellipses
def distanceCenters(ellipse1,ellipse2):
    distance = math.sqrt(math.pow((ellipse1[0][0]-ellipse2[0][0]),2) +math.pow((ellipse1[0][1]-ellipse2[0][1]),2))
    return distance

#function that detects if 2 or more circles are nested
def detNested(rawCircles):
    size = len(rawCircles)
    nestedCircles = np.empty(size,object)
    nestedCnt = 0
    for i in xrange(0,size):
        nested = False
        for j in xrange(i, size):
            if i !=j:
                circle1 = rawCircles[i]
                circle2 = rawCircles[j]

                radius1 = (circle1[1][0] + circle1[1][1]) /2.0
                radius2 = (circle2[1][0] + circle2[1][1]) /2.0

                distance = distanceCenters(circle1,circle2)

                if(distance < math.fabs(radius1 - radius2)):
                    nested = True

        if nested:
            nestedCircles[nestedCnt] = rawCircles[i]
            nestedCnt += 1

    nestedCircles = np.resize(nestedCircles,nestedCnt)

    return nestedCircles

def checkEcc(ellipse,threshold):
    if ellipse[1][0] *1.0/ellipse[1][1] >threshold:
        return True
    return False

def findCommonCent(nestedCircles):
    size = len(nestedCircles)

    for i in xrange(0,size):
        baseCircle = nestedCircles[i]
        smallestRadius = (baseCircle[1][0] + baseCircle[1][1] /2.0)
        smallest = i

        for j in xrange(i,size):
            circle = nestedCircles[j]
            radius = (circle[1][0] + circle[1][1]) /2.0
            if(radius < smallestRadius):
                smallestRadius = radius
                smallest = j
        nestedCircles[i] = nestedCircles[smallest]
        nestedCircles[smallest] = baseCircle

    conCombos = np.empty([size,size],object)

    maxConCnt = 1
    maxConIndex = 0

    xSum = np.zeros(size)
    ySum = np.zeros(size)

    for i in xrange(size-1,0,-1):
        outer = nestedCircles[i]
        conCombos[i][0] = outer
        cnt = 1

        for j in xrange(i,0,-1):
            inner = nestedCircles[j]
            
            if(distanceCenters(outer,inner)<15) and (i != j):

                previous = conCombos[i][cnt-1]
                radPrev = (previous[1][0]+previous[1][1]) /2.0
                radCurr = (inner[1][0] + inner[1][1]) /2.0

                if (radPrev - radCurr) >2:
                    conCombos[i][cnt] = inner

                    xSum[i] += [0][0]
                    ySum[i] += inner[0][1]

                    cnt += 1
        
        if(cnt > maxConCnt):
            maxConCnt = cnt
            maxConIndex = i


    if(maxConCnt < 5):
        return None,None

    mostCon = conCombos[maxConIndex]
    mostCon = np.resize(mostCon,maxConCnt)

    meanCenter = xSum[maxConIndex]/(maxConCnt -1), ySum[maxConIndex]/(maxConCnt -1)

    return mostCon , meanCenter

def tagAspectRatio(target):
    size = len(target)
    ratios = np.empty(size-1,float)
    cnt = 0

    for i in xrange(0,size-1):
        circle1 = target[i]
        circle2 = target[i+1]
        radius1 = (circle1[1][0] +circle1[1][1]) /2.0
        radius2 = (circle2[1][0] +circle2[1][1]) /2.0

        ratio = radius2 /radius1
        ratios[cnt] = round(ratio,3)
        cnt += 1
    return ratios

def calcRingSize(ringNumber):
    radius = .0975
    target_code =[0.8,0.91,0.76,0.84,0.7,0.66,0.49]

    for i in xrange(0,ringNumber):
        radius= radius * target_code[i]

    return radius

def pixels_to_angle(num_pixels,fov,img_size):
    return num_pixels * math.radians(fov)/img_size

def get_distance_from_pixels(size_in_pixels,actual_size,fov,img_size):
    if (size_in_pixels == 0):
        return 9999.9
    return actual_size / pixels_to_angle(size_in_pixels,fov,img_size)

def CalcDistanceTarget(target,ratios):
    distance = 0
    readings = 0
    n=0
    target_code =[0.8,0.91,0.76,0.84,0.7,0.66,0.49]
    for i in xrange(0,len(ratios)):
        ratio = ratios[i]
        for j in xrange(0,len(target_code)):
            if(math.fabs(target_code[j] -ratio) <= .015):
                circle1 = target[i]
                circle2 = target[i+1]
                radius1 = (circle1[1][0] + circle1[1][1]) /2.0
                radius2 = (circle2[1][0] + circle2[1][1]) /2.0
                fov = 33
                img_size = math.sqrt(1280**2 +720**2)

                dist1 = get_distance_from_pixels(radius1,calcRingSize(j), fov, img_size)
                dist2 = get_distance_from_pixels(radius2,calcRingSize(j+1),fov,img_size)
                distance += (dist1 +dist2) /2.0
                readings += 1
    if(readings ==0):
        return -1
    return distance/(readings * 1.0)

if __name__ == "__main__":
    cam = cv2.VideoCapture(1)
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
    cv2.namedWindow('edges')
    cv2.namedWindow('Threshold')
    cv2.createTrackbar('Thresh','Threshold',0,250,nothing)
    while True:
        ret,img = cam.read()
        results = search_frame(img)
        cv2.imshow('img', img)
        cv2.waitKey(1)
