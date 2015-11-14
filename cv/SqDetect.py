import cv2
 
  
# load the video
camera = cv2.VideoCapture(1)
   
# keep looping
while True:
    # grab the current frame and initialize the status text
    (grabbed, frame) = camera.read()
    status = "No Targets"
                                     
        # convert the frame to grayscale, blur it, and detect edge
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blurred, 50, 110)
                                                     
        # find contours in the edge map
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
            
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)

        if len(approx) >=4 and len(approx) <=10:
                    
            (x, y, w, h) = cv2.boundingRect(approx)
            aspectRatio = w/ float(h)

            area = cv2.contourArea(c)
            hullArea=cv2.contourArea(cv2.convexHull(c))
            solidity = area / float(hullArea)

            keepDims = w >25 and h > 25
            keepSolidity = solidity > 0.75
            keepAspectRatio = aspectRatio >=.85 and aspectRatio <=1.15

            if keepDims and keepSolidity and keepAspectRatio:
                        
                cv2.drawContours(frame, [approx], -1, (0,0,255),4)
                status = "WE GOTS A TARGET!"

                M = cv2.moments(approx)
                (cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                (startX, endX) = (int(cX - (w * 0.15)), int(cX + (w * 0.15)))
                (startY, endY) = (int(cY - (h * 0.15)), int(cY + (h * 0.15)))
                cv2.line(frame, (startX, cY), (endX, cY), (0, 0, 255), 3)
                cv2.line(frame, (cX, startY), (cX, endY), (0, 0, 255), 3)

    cv2.putText(frame, status, (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0) , 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edged)

    key = cv2.waitKey(1) & 0xFF

    if key==ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
