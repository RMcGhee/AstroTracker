import math

hyp = 50
az_dist = 40
alt_dist = 30
theo_angle = math.atan(30/40)
angle_off = math.radians(-10)
real_angle = theo_angle - angle_off
real_alt = hyp * math.sin(real_angle)
real_az = hyp * math.cos(real_angle)

print('theo: {}, offset: {}, real: {}'.format(theo_angle, angle_off, real_angle))
print('az: {}, alt: {}, real az: {}, real alt: {}'.format(
    az_dist, alt_dist, real_az, real_alt
))