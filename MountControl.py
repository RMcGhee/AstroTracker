# Program that manages the alt and az of the mount.
from AltitudeAzimuth import *
import ephem
import time
import math
import threading

MOUNT_LOCK = threading.Lock()

class Mount():
    'Mount is the object which contains the information for, as well'
    'as controls the mount. It has three axes.'
    'Axis pan moves the mount left and right.'
    'Axis tilt moves the mount up and down.'
    'Axis roll rotates the mount along the direction of the lens.'
    
    def __init__(self, update_interval, location):
        'do the __init__ things'
        self.update_interval = update_interval
        self.location = location
        self.curr_az = 0.0 # is the az axis, [0,360), in the rotated frame, in radians
        self.curr_alt = 0.0 # is the alt axis, [-90, 90], in the rotated frame, in rads
        self.curr_roll = 0.0 # The current rotation of the roll axis, in rads
        self.rad_step_pan = 0.00002 #radians per step when panning
        self.rad_step_tilt = 0.00002 #radians per step when tilting
        self.rad_step_roll = 0.0001 #radians per step when rolling
        self.number_ref_points = 0  # reference points are used to refine the degrees
                                    # per step for the mount.
        self.rad_offset = math.radians(2) # radians of offset, calculated when calibrated.
        self.tcnp = {'Az': 0.0, 'Alt': 0.0} 
                    # true celestial north pole. coords are given as {az, alt}
        self.is_calibrated = True
        self.done_moving = True
        
    def goto_coords(self, coords):
        'Given a set of coordinates in RA/DEC format, move mount to said coordinates'
        'If do_track is set, goto_coords makes call to run() at said coords, after goto'
        'completes the move. run() will continue to track at this location until'
        'an interrupt call is recieved. Interrupt can stop the tracking, or just'
        'move the mount to a new location to track at. do_track cannont be True'
        'if a proper calibration has not been done.'
        'If the move takes a long time, az/alt may be wrong when goto_coords completes'
        'If tracking, get az/alt coords again, make another move to catch up. Then'
        'start tracking.'
        ra = ephem.hours(coords[0]) # ephem is not exposed to AstroTracker.
        dec = ephem.degrees(coords[1]) # Astro tracker will send coords as strings.
        next_loc = TrackMe(self.location, ra, dec)
        
        # get_az_alt returns a dict for {Az, Alt}
        next_az_alt = next_loc.get_az_alt(0)
        pan_tilt_moves = self.get_moves(next_az_alt['az'], next_az_alt['alt'])
        # moves are always ints. can be negative to indicate move in opposite direction. 
        # due to the fineness of each step, a small amount
        # of inaccuracy is fine. the true az/alt of the move is stored in pan_axis,
        # tilt_axis, and roll_axis. This prevents small errors from snowballing, as
        # any small errors will be negated in subsequent moves. Due to the nature
        # of truncating a float, moves will always end up within one step of the
        # true destination.
        
        # make moves until within 1 of true destination.
        # Each of these methods runs in their own thread, with no delay other than
        # the time required to make each move.
        while(pan_tilt_moves['pan'] != 0 or pan_tilt_moves['tilt'] != 0):
            print('\nNumber of pan moves: {}\nNumber of tilt moves: {}'.format(
                pan_tilt_moves['pan'], pan_tilt_moves['tilt']
            ))
            rotated_given = self.get_offset_coords(next_az_alt['az'], next_az_alt['alt'])
            print('\nGiven Az:\t{}\tAlt: {}'
                '\nCurrent Az:\t{}\tAlt: {}\n'
                'Rotated Az:\t{}\tAlt: {}'.format(
                    math.degrees(next_az_alt['az']), math.degrees(next_az_alt['alt']),
                    math.degrees(self.curr_az), math.degrees(self.curr_alt),
                    math.degrees(rotated_given['az']), math.degrees(rotated_given['alt'])
                ))
            
            pan_thread = threading.Thread(target=self.pan, args=
                (pan_tilt_moves['pan'], 0.0))
            tilt_thread = threading.Thread(target=self.tilt, args=
                (pan_tilt_moves['tilt'], 0.0))
            pan_thread.setDaemon(True)
            tilt_thread.setDaemon(True)
            pan_thread.start()
            tilt_thread.start()
            pan_thread.join()          
            tilt_thread.join()
            
            next_az_alt = next_loc.get_az_alt(0)
            pan_tilt_moves = self.get_moves(next_az_alt['az'], next_az_alt['alt'])
            time.sleep(0.1)
        rotated_given = self.get_offset_coords(next_az_alt['az'], next_az_alt['alt'])
        print('\nGiven Az:\t{}\tAlt: {}'
            '\nCurrent Az:\t{}\tAlt: {}\n'
            'Rotated Az:\t{}\tAlt: {}'.format(
                math.degrees(next_az_alt['az']), math.degrees(next_az_alt['alt']),
                math.degrees(self.curr_az), math.degrees(self.curr_alt),
                math.degrees(rotated_given['az']), math.degrees(rotated_given['alt'])
            ))

    def track_object(self, coords):
        self.goto_coords(coords)
        do_track = True
        pan_delay = 0.0
        tilt_delay = 0.0
        print('*************\nStarting the tracking now!\n*****************')
        while(do_track):
            ra = ephem.hours(coords[0]) # ephem is not exposed to AstroTracker.
            dec = ephem.degrees(coords[1]) # Astro tracker will send coords as strings.
            next_loc = TrackMe(self.location, ra, dec)
            next_az_alt = next_loc.get_az_alt(1)
            # get_az_alt returns a dict for {Az, Alt}, offset is 1 second
            pan_tilt_moves = self.get_moves(next_az_alt['az'], next_az_alt['alt'])
            if(pan_tilt_moves['pan'] != 0):
                pan_delay = math.fabs(self.update_interval / pan_tilt_moves['pan'])
            else:
                pan_delay = 1.0
            if(pan_tilt_moves['tilt'] != 0):
                tilt_delay = math.fabs(self.update_interval / pan_tilt_moves['tilt'])
            else:
                tilt_delay = 1.0
            
            pan_thread = threading.Thread(target=self.pan, args=
                (pan_tilt_moves['pan'], pan_delay))
            tilt_thread = threading.Thread(target=self.tilt, args=
                (pan_tilt_moves['tilt'], tilt_delay))
            pan_thread.setDaemon(True)
            tilt_thread.setDaemon(True)
            pan_thread.start()
            tilt_thread.start()
            pan_thread.join()          
            tilt_thread.join()
            print('Round done.')
            rotated_given = self.get_offset_coords(next_az_alt['az'], next_az_alt['alt'])
            print('\nGiven Az:\t{}\tAlt: {}'
                '\nCurrent Az:\t{}\tAlt: {}\n'
                'Rotated Az:\t{}\tAlt: {}'.format(
                    math.degrees(next_az_alt['az']), math.degrees(next_az_alt['alt']),
                    math.degrees(self.curr_az), math.degrees(self.curr_alt),
                    math.degrees(rotated_given['az']), math.degrees(rotated_given['alt'])
                ))
    
    def get_moves(self, dest_az, dest_alt):
        'finds shortest path to destination, rolls over azimuth if over 360'
        'uses rot_coords to get rotated coordinates needed for the move.'
        'calculates the number of steps for pan and tilt needed.'
        
        rot_coords = self.get_offset_coords(dest_az, dest_alt)
            #offset_coords returns alt and az in radians
        dif_az = rot_coords['az'] - self.curr_az
        dif_alt = rot_coords['alt'] - self.curr_alt
        # if dif > 180, go backwards to destination.
        if(dif_az > (math.pi)):
            az_move = dif_az - (2 * math.pi)
        # if dif < -180, go forwards to destination.
        elif(dif_az < -(math.pi)):
            az_move = 360 - (2 * math.pi)
        else:
            az_move = dif_az

        alt_move = dif_alt
        step_pan = int(az_move / self.rad_step_pan)
        step_tilt = int(alt_move / self.rad_step_tilt)
        
        return {'pan': step_pan, 'tilt': step_tilt}

    def pan(self, num_moves, delay_secs):
        'num_moves is an int, delay_secs is a float with the delay. a delay of'
        '0.0 seconds means no delay, other than the time required to make a move.'

        print('pan: {}'.format(num_moves))
        if(num_moves < 0):
            dir_step_pan = -self.rad_step_pan
        else:
            dir_step_pan = self.rad_step_pan
        
        for i in range(0, abs(num_moves)):
            MOUNT_LOCK.acquire()
            self.curr_az += dir_step_pan
            # do the move.
            MOUNT_LOCK.release()
            time.sleep(0.00001 + delay_secs)
        # rollover azimuth if outside of [0,360)
        if(self.curr_az >= (2 * math.pi)):
            self.curr_az -= (2 * math.pi)
        elif(self.curr_az < 0):
            self.curr_az += (2 * math.pi)

    def tilt(self, num_moves, delay_secs):
        'num_moves is an int, delay_secs is a float with the dealy. a delay of'
        '0.0 seconds means no delay, other than the time required to make a move.'
        
        print('tilt: {}'.format(num_moves))
        if(num_moves < 0):
            dir_step_tilt = -self.rad_step_tilt
        else:
            dir_step_tilt = self.rad_step_tilt

        for i in range(0, abs(num_moves)):
            MOUNT_LOCK.acquire()
            self.curr_alt += dir_step_tilt
            # do the move.
            MOUNT_LOCK.release()
            time.sleep(0.00001 + delay_secs)

    def get_offset_coords(self, az, alt):
        'The nature of the horizontal coordinate system is such that:'
        '0 <= az < 360'
        '-90 <= alt <= 90'
        'Catch divide by zero, otherwise arctan works fine.'
        
        hyp = math.sqrt(az ** 2 + alt ** 2)
        if(az == 0):
            ref_angle = math.radians(90)
        else:
            ref_angle = math.atan(alt/az)
        real_angle = ref_angle - self.rad_offset
        
        rot_az = hyp * math.cos(real_angle)
        rot_alt = hyp * math.sin(real_angle)
        
        if(rot_az < 0):
            rot_az = (2 * math.pi) + rot_az
        elif(rot_az > (2 * math.pi)):
            rot_az = rot_az - (2 * math.pi)
        if(rot_alt > (math.pi / 2)):
            rot_alt = (-math.pi / 2) - rot_alt
        elif(rot_alt < (-math.pi / 2)):
            rot_alt = (math.pi / 2) - rot_alt
        return {'az': rot_az, 'alt': rot_alt}
        
    
# ra = ephem.hours('5:35:24')
# dec = ephem.degrees('-5:27:00:0')
# coords = [ra, dec]
# location = ["38.9517", "-92.3341", 219]
# camera_mount = Mount(1, location)
# camera_mount.track_object(coords)