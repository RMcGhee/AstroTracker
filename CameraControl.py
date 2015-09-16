import threading

CAMERA_LOCK = threading.Lock()

class Camera():
    'provides an interface for controlling a camera shutter. can control shutter'
    'speed (time open), delay between shutters, delay before starting the interval'
    'and number of frames to take.'
    def __init__(self):
        'make the standard variables. delay_frames min depends on the time it takes'
        'for a camera to save a file, get ready for next frame. this time is usually'
        'longer when an exposure is longer than 1 sec.'
        'Reasonable input is not checked by this program, but by AstroTracker.py instead,'
        'which provides input.'
        self.shutter_speed = 1.0
        self.number_frames = 1 
        self.delay_start = 0 
        self.delay_frames = 3 
        self.frames_shot = 0
    def set_params(self, shutter_speed, num_frames, delay_start, delay_bet):
        self.shutter_speed = shutter_speed
        self.number_frames = number_frames
        self.delay_start = delay_start
        self.delay_bet = delay_bet
    
    