'AstroTracker.py is the program that displays the GUI and moderates the other portions'
'of the program. The main meat of the astro tracking is done in MountControl, '
'AlititudeAzimuth, and MotorControl. CameraControl is a glorified intervalometer.'

# Need to finish GUI, work on calibration

from tkinter import *
import tkinter.ttk as ttk
import os
import threading
import time
from MountControl import *
import InputManagement

root = Tk()

#screen height and width will be determined by the screen you are using. If you're
# using something other than a RaspberryPi with a tiny screen, you may want to change
# the number entry interface. It is targeted to a touchscreen device.
screen_width = 320
screen_height = 240
x_win_coord = 200
y_win_coord = 200

#minimum_shutter_speed is determined by your camera. Change to your liking, although
# negative numbers should be avoided. 
minimum_shutter_speed = 1/1000

ready_to_shoot = False
c_mount = Mount(update_interval=1, location=["38.9517", "-92.3341", 219])

i_manage = InputManagement.InputManagement()
root.geometry('{}x{}+{}+{}'.format(screen_width, screen_height, x_win_coord, y_win_coord))
root.title('AST3K')
    # yes, its a reference to that show.
    # no, not that one, the other one.
    # the one with the robots.
    # yes, Futurama.

pan_tilt_frame = Frame(root)
menu_frame = Frame(root)
track_object_frame = Frame(root)
camera_control_frame = Frame(root)
number_entry_frame = Frame(root)
calibrate_frames = dict(dia1=Frame(root), dia2=Frame(root), landmarks=Frame(root))

def make_track_object_frame(use_frame):
    use_frame.grid(column=0, row=0, sticky='nsew')
    
    l_set_RA = Label(use_frame, text='Set Right Ascension: ')
    l_set_DEC = Label(use_frame, text='Set Declination: ')
    l_adjust_coords = Label(use_frame, text='Adjust coordinates: ')
    l_moving_to = Label(use_frame, text='Moving to object', state=DISABLED)
    
    b_back = Button(use_frame, text='<-Back', command=lambda: menu_frame.tkraise())
    b_set_RA = Button(use_frame, text='12.23.34', 
        command=lambda: i_manage.call_number_frame(b_set_RA, 'RA_Degrees'))
    b_set_DEC = Button(use_frame, text='Set DEC', 
        command=lambda: i_manage.call_number_frame(b_set_DEC, 'DEC_Degrees'))
    b_adjust_coords = Button(use_frame, text='Adjust Coordinates',
        command=lambda: i_manage.call_pan_frame(use_frame))
    b_start_track = Button(use_frame, text='Start track', 
        command=lambda: make_move(l_moving_to, b_set_RA, b_set_DEC))
    b_stop_track = Button(use_frame, text='Stop track')
    
    b_back.grid(column=0, row=0, sticky='w')
    b_set_RA.grid(column=1, row=1, sticky='w')
    b_set_DEC.grid(column=1, row=2, sticky='w')
    b_adjust_coords.grid(column=1, row=3, sticky='w')
    b_start_track.grid(column=0, row=4, sticky='ew')
    b_stop_track.grid(column=1, row=4, sticky='ew')
    
    l_set_RA.grid(column=0, row=1, sticky='e')
    l_set_DEC.grid(column=0, row=2, sticky='e')
    l_adjust_coords.grid(column=0, row=3, sticky='e')
    l_moving_to.grid(column=1, row=0, sticky='w')

    use_frame.grid_columnconfigure(0, minsize=(screen_width/2))
    use_frame.grid_columnconfigure(1, minsize=(screen_width/2))

    for i in range(0, 5):
        use_frame.grid_rowconfigure(i, minsize=(screen_height/5))
    
    i_manage.set_pan_frame_buttons(RA_button=b_set_RA, DEC_button=b_set_DEC)
    
    
def make_pan_tilt_frame(use_frame):
    use_frame.grid(column=0, row=0, sticky='nsew')

    b_single_up = Button(use_frame, text='^', command=lambda: c_mount.tilt(10, 0.0))
    b_double_up = Button(use_frame, text='^^', command=lambda: c_mount.tilt(100, 0.0))
    b_single_down = Button(use_frame, text='v', command=lambda: c_mount.tilt(-10, 0.0))
    b_double_down = Button(use_frame, text='vv', command=lambda: c_mount.tilt(-100, 0.0))
    b_single_right = Button(use_frame, text='>', command=lambda: c_mount.pan(10, 0.0))
    b_double_right = Button(use_frame, text='>>', command=lambda: c_mount.pan(100, 0.0))
    b_single_left = Button(use_frame, text='<', command=lambda: c_mount.pan(-10, 0.0))
    b_double_left = Button(use_frame, text='<<', command=lambda: c_mount.pan(-100, 0.0))
    b_set = Button(use_frame, text='Track!')
    b_back = Button(use_frame, text='<-Back', 
        command=lambda: i_manage.close_pan_frame())

    b_single_up.grid(column=2, row=1, sticky='ew')
    b_double_up.grid(column=2, row=0, sticky='ew')
    b_single_down.grid(column=2, row=3, sticky='ew')
    b_double_down.grid(column=2, row=4, sticky='ew')
    b_single_right.grid(column=3, row=2, sticky='ew')
    b_double_right.grid(column=4, row=2, sticky='ew')
    b_single_left.grid(column=1, row=2, sticky='ew')
    b_double_left.grid(column=0, row=2, sticky='ew')
    b_set.grid(column=2, row=2, sticky='ew')
    b_back.grid(column=0, row=0, sticky='ew')
    
    for i in range(0, 5):
        use_frame.grid_columnconfigure(i, minsize=(screen_width/5))
    for i in range(0, 5):
        use_frame.grid_rowconfigure(i, minsize=(screen_height/5))
    
    i_manage.pan_frame = use_frame
    i_manage.set_pan_frame_buttons(b_back=b_back, b_center=b_set)

    
def make_camera_control_frame(use_frame):
    use_frame.grid(column=0, row=0, sticky='nsew')
    
    b_shutter_speed = Button(use_frame, text='value > {}'.format(minimum_shutter_speed),
        command=lambda: i_manage.call_number_frame(b_shutter_speed, 
            'FloatNoNeg', min_val=minimum_shutter_speed))
    
    b_number_frames = Button(use_frame, text='value > 0',
        command=lambda: i_manage.call_number_frame(b_number_frames, 'Int', min_val=1))

    b_delay_bet = Button(use_frame, text='value >= 2.0',
        command=lambda: i_manage.call_number_frame(b_delay_bet, 
            'FloatNoNeg', min_val=2.0))

    b_delay_start = Button(use_frame, text='value > 5.0',
        command=lambda: i_manage.call_number_frame(b_delay_start,
            'FloatNoNeg', min_val=5.0))

    b_back = Button(use_frame, text='<-Back',
        command=lambda: menu_frame.tkraise())
    b_start_track = Button(use_frame, text='Start Shooting!')
    b_stop_track = Button(use_frame, text='STOP Shooting!', bg='red')
    
    l_shutter_speed = Label(use_frame, text='Shutter Speed: ')
    l_number_frames = Label(use_frame, text='Number of frames: ')
    l_delay_bet = Label(use_frame, text='Delay between frames: ')
    l_delay_start = Label(use_frame, text='Delay before start: ')
    
    l_shutter_speed.grid(column=0, row=1, columnspan=2, sticky='e')
    l_number_frames.grid(column=0, row=2, columnspan=2, sticky='e')
    l_delay_bet.grid(column=0, row=3, columnspan=2, sticky='e')
    l_delay_start.grid(column=0, row=4, columnspan=2, sticky='e')
    
    b_shutter_speed.grid(column=2, row=1, sticky='ew')
    b_number_frames.grid(column=2, row=2, sticky='ew')
    b_delay_bet.grid(column=2, row=3, sticky='ew')
    b_back.grid(column=0, row=0, sticky='ew')
    b_delay_start.grid(column=2, row=4, sticky='ew')
    b_start_track.grid(column=0, row=5, sticky='ew')
    b_stop_track.grid(column=1, row=5, columnspan=1, sticky='ew')
    
    for i in range(0, 4):
        use_frame.grid_columnconfigure(i, minsize=(screen_width/4))
    
    for i in range(0, 6):
        use_frame.grid_rowconfigure(i, minsize=(screen_height/6))

    
def make_number_entry_frame(use_frame):
    use_frame.grid(column=0, row=0, sticky='nsew')
    num_entry_stack = []
    
    enter_text = Entry(use_frame)
    b_one = Button(use_frame, text='1', 
        command=lambda: i_manage.enter_number('1'))
    b_two = Button(use_frame, text='2', 
        command=lambda: i_manage.enter_number('2'))
    b_three = Button(use_frame, text='3', 
        command=lambda: i_manage.enter_number('3'))
    b_four = Button(use_frame, text='4', 
        command=lambda: i_manage.enter_number('4'))
    b_five = Button(use_frame, text='5', 
        command=lambda: i_manage.enter_number('5'))
    b_six = Button(use_frame, text='6', 
        command=lambda: i_manage.enter_number('6'))
    b_seven = Button(use_frame, text='7', 
        command=lambda: i_manage.enter_number('7'))
    b_eight = Button(use_frame, text='8', 
        command=lambda: i_manage.enter_number('8'))
    b_nine = Button(use_frame, text='9', 
        command=lambda: i_manage.enter_number('9'))
    b_zero = Button(use_frame, text='0', 
        command=lambda: i_manage.enter_number('0'))
    b_period = Button(use_frame, text='.', 
        command=lambda: i_manage.enter_number('.'))
    b_done = Button(use_frame, text='Done', 
        command=lambda: i_manage.close_number_frame())
    b_delete = Button(use_frame, text='Del', 
        command=lambda: i_manage.delete_digit())
    b_neg = Button(use_frame, text='Negative',
        command=lambda: i_manage.enter_number('-'), state=DISABLED)
    
    enter_text.grid(column=0, row=0, sticky='ew', columnspan=3)
    b_one.grid(column=0, row=1, sticky='ew')
    b_two.grid(column=1, row=1, sticky='ew')
    b_three.grid(column=2, row=1, sticky='ew')
    b_four.grid(column=0, row=2, sticky='ew')
    b_five.grid(column=1, row=2, sticky='ew')
    b_six.grid(column=2, row=2, sticky='ew')
    b_seven.grid(column=0, row=3, sticky='ew')
    b_eight.grid(column=1, row=3, sticky='ew')
    b_nine.grid(column=2, row=3, sticky='ew')
    b_zero.grid(column=1, row=4, sticky='ew')
    b_period.grid(column=2, row=4, sticky='ew')
    b_delete.grid(column=0, row=4, sticky='ew')
    b_done.grid(column=1, row=5, sticky='ew', columnspan=2)
    b_neg.grid(column=0, row=5, sticky='ew', columnspan=1)
    
    for i in range(0, 3):
        use_frame.grid_columnconfigure(i, minsize=(screen_width/3))
    for i in range(0, 6):
        use_frame.grid_rowconfigure(i, minsize=(screen_height/6))
    
    i_manage.set_text_box(enter_text)
    i_manage.numpad_frame = use_frame
    i_manage.set_neg_button(b_neg)

    
def make_menu_frame(use_frame):
    use_frame.grid(row=0, column=0, sticky='nsew')
    
    go_pan_tilt = Button(use_frame, text='Pan and Tilt', 
        command=lambda: i_manage.call_pan_frame(use_frame))
    go_track_menu = Button(use_frame, text='Track Object', 
        command=lambda: track_object_frame.tkraise())
    go_camera_control_frame = Button(use_frame, text='Camera Control', 
        command=lambda: camera_control_frame.tkraise())
    go_number_entry_frame = Button(use_frame, text='Calibrate', 
        command=lambda: calibrate_frames['dia1'].tkraise())
    b_exit = Button(use_frame, text='Exit', 
        command=lambda: close_all())
        
    go_pan_tilt.grid(column=0, row=0, sticky='ew')
    go_track_menu.grid(column=1, row=0, sticky='ew')
    go_camera_control_frame.grid(column=0, row=1, sticky='ew')
    go_number_entry_frame.grid(column=1, row=1, sticky='ew')  
    b_exit.grid(column=1, row=5, sticky='ew')
    
    use_frame.grid_columnconfigure(0, minsize=(screen_width/2))
    use_frame.grid_columnconfigure(1, minsize=(screen_width/2))

    for i in range(0, 6):    
        use_frame.grid_rowconfigure(i, minsize=(screen_height/6))


def make_calibrate_frames(frames):
    dia_1 = frames['dia1']
    dia_2 = frames['dia2']
    lmarks = frames['landmarks']
    
    dia_1.grid(row=0, column=0, sticky='nsew')
    dia_2.grid(row=0, column=0, sticky='nsew')    
    lmarks.grid(row=0, column=0, sticky='nsew')
        
    calibration_dia1 = 'This step calibrates your mount to be level and '\
    'pointed approximately north. You will use pan/tilt/rotation controls '\
    'to accomplish this. Click next to continue.'
    calibration_dia2 = 'This step uses well known stars to calibrate the mount '\
    'for accurate tracking. After selecting a landmark star, you will use '\
    'pan/tilt controls to place the landmark star in the center of your camera '\
    'frame. Once centered, press the center button to lock the coordinates. You '\
    'will do this for three landmarks.'
    
    dia_1.grid(row=0, column=0, sticky='nsew')
    dia_2.grid(row=0, column=0, sticky='nsew')
    lmarks.grid(row=0, column=0, sticky='nsew')
    
    b_back_dia1 = Button(dia_1, text='<-')
    b_next_dia1 = Button(dia_1, text='Next ->', 
        command=lambda: i_manage.call_pan_frame(dia_2, 'dia_2'))
    l_dia_dia1 = Label(dia_1, text=calibration_dia1)
    l_dia_dia1['height'] = 5
    l_dia_dia1['wraplength'] = 320
    
    b_back_dia1.grid(column=0, row=0, sticky='ew')
    b_next_dia1.grid(column=3, row=5, sticky='ew')
    l_dia_dia1.grid(column=0, row=1, sticky='ns', columnspan=4, rowspan=4)
    
    b_back_dia2 = Button(dia_2, text='<-', command=lambda: menu_frame.tkraise())
    b_next_dia2 = Button(dia_2, text='Next ->', 
        command=lambda: lmarks.tkraise())
    l_dia_dia2 = Label(dia_2, text=calibration_dia2)
    l_dia_dia2['height'] = 5
    l_dia_dia2['wraplength'] = 300
    
    b_back_dia2.grid(column=0, row=0, sticky='ew')
    b_next_dia2.grid(column=3, row=5, sticky='ew')
    l_dia_dia2.grid(column=0, row=1, sticky='ns', columnspan=4, rowspan=4)
    
    for i in range(0,6):
        dia_1.grid_rowconfigure(i, minsize=(screen_height/6))
    for i in range(0,4):
        dia_1.grid_columnconfigure(i, minsize=(screen_width/4))
    for i in range(0,6):
        dia_2.grid_rowconfigure(i, minsize=(screen_height/6))
    for i in range(0,4):
        dia_2.grid_columnconfigure(i, minsize=(screen_width/4))    
    
    
def close_all():
    exit()

def make_move(l_moving=None, b_RA=None, b_DEC=None):
    RA = b_RA['text']
    DEC = b_DEC['text']
    if('Set' in RA or 'Set' in DEC):
        return

    l_moving.config(state=NORMAL)
    coords = (RA, DEC)
    move = threading.Thread(target=c_mount.goto_coords, args=(coords,))
    move.setDaemon(True)
    move.start()

    while(move.is_alive()):
        l_moving.config(state=NORMAL)
        l_moving.update()
        time.sleep(0.3)
        l_moving.config(state=DISABLED)
        l_moving.update()
        time.sleep(0.3)


make_pan_tilt_frame(pan_tilt_frame)
make_menu_frame(menu_frame)
make_number_entry_frame(number_entry_frame)
make_camera_control_frame(camera_control_frame)
make_track_object_frame(track_object_frame)
make_calibrate_frames(calibrate_frames)
menu_frame.tkraise()

# use only on mac, otherwise use lift on window.
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost ''' +
            '''of process "Python" to true' ''')
root.mainloop()
