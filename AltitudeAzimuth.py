# Mostly done, some other math for calibration will be done here.

from ephem import *
import time

class TrackMe():
    'TrackMe makes an object with a set location, RA, and DEC'
    'Using these, when its get_alt_az function is called, it'
    'returns the alt and az of where it is going to be at time'
    'gmt + offset_sec'
    
    def __init__(self, location, right_as, decl):
        'location is a list that contains:'
        'latitude, longitude, and elevation'
        'longitude is negative if it is given as number W'
        'right_as is given in hours string format xx:xx:xx'
        'decl is given in degrees string format xx:xx:xx'
        self.body = FixedBody()
        self.body._ra = hours(right_as)
        self.body._dec = degrees(decl)
        self.obs = Observer()
        self.obs.lat = location[0]
        self.obs.lon = location[1]
        self.obs.elevation = location[2]
        
    def get_az_alt(self, offset_sec):
        'offset_sec must be given in seconds (int)'
        'in the scale of seconds, a straight line move'
        'can approximate the curve necessary to track a celestial'
        'object.'
        # Get time in gmtime format, then Date() format
        # Then add any offset seconds supplied.
        next_time = time.gmtime(time.time())
        next_time = Date(time.strftime("%Y/%m/%d %H:%M:%S", next_time))
        next_time = Date(next_time + (offset_sec * second))
        self.obs.date = Date(next_time)
        print('Time: {}'.format(self.obs.date))
        self.body.compute(self.obs)
        return {'az': self.body.az, 'alt': self.body.alt}

def main():
    ra = hours('19:50:47')
    dec = degrees('8:42:12')
    location = ["38.9517", "-92.3341", 219]
    tester = TrackMe(location, ra, dec)
    for i in range(0,2):
        to_p = tester.get_az_alt(0)
        time.sleep(2)

if __name__ == '__main__':
    main()
