from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
from pyorbital import tlefile
'''
tle = tlefile.read('noaa 18', '../tle/noaa18_June_14_2018.txt')
print(tle.inclination)
'''
# Use current TLEs from the internet:
orb = Orbital("NOAA 19")

#sup_SDRSharp_20180614_202010Z_137850000Hz_IQ_f1
#m1_SDRSharp_20180615_141220Z_137300000Hz_IQ_f1.png
tc = datetime(2018, 6, 15, 14, 12, 20)
tc = tc + timedelta(seconds=int(925/4))
now = datetime.utcnow()
# Get normalized position and velocity of the satellite:
print(orb.get_position(tc))
print(orb.get_lonlatalt(tc))