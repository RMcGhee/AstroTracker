#MotorControl controls the motors used on the mount. These motors are threaded
#to allow moves in all three directions at the same time.
#this will be worked on when the hardware integration starts.
import math
import threading

MOTOR_LOCK = threading.Lock()

class MotorControl():
    
    def __init__(self):
        
