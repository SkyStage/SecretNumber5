from dronekit import connect
import cv2
import numpy as np
import math





def get_bg(self,v_roll, v_pitch):
    image = np.zeros((320,640,3),np.uint8)
    image[:] = (232,228,227)

    

