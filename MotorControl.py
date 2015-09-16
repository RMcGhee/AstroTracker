#MotorControl controls the motors used on the mount. These motors are threaded
#to allow moves in all three directions at the same time.

import math
import threading

MOTOR_LOCK = threading.Lock()

class MotorControl():
    
    def __init__(self):
        