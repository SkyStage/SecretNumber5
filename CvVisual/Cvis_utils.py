import math
from dronekit from dronekit

def rotate_xy(x,y,angle):
    cos_ang = math.cos(angle)
    sin_ang = math.sin(angle)
    x_centered = x - 640
    y_centered = y- 320
    x_rotated = x *cos_ang - y * sin_ang
    y_rotated = x *sin_ang + y * cos_ang
    return x_rotated, y_rotated
