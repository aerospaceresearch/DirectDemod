from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
from pyorbital import tlefile
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy import ndimage
from PIL import Image
from scipy import misc

def angleFromCoordinate(lat1, long1, lat2, long2):
    # source: https://stackoverflow.com/questions/3932502/calculate-angle-between-two-latitude-longitude-points
    lat1 = np.radians(lat1)
    long1 = np.radians(long1)
    lat2 = np.radians(lat2)
    long2 = np.radians(long2)

    dLon = (long2 - long1)

    y = np.sin(dLon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dLon)
    brng = np.arctan2(y, x)
    brng = np.degrees(brng)
    brng = (brng + 360) % 360
    brng = 360 - brng
    return brng

orb = Orbital("NOAA 19", tle_file='../tle/noaa18_June_14_2018.txt')
tc = datetime(2018, 6, 15, 14, 7, 52)

im = plt.imread('m3.png')
im = im[:,85:995]
oim = im[:]
print(im.shape)

tdelta = int(im.shape[0]/16)

top = orb.get_lonlatalt(tc + timedelta(seconds=int(im.shape[0]/4) - tdelta))[:2][::-1]
bot = orb.get_lonlatalt(tc + timedelta(seconds=int(im.shape[0]/4) + tdelta))[:2][::-1]
center = orb.get_lonlatalt(tc + timedelta(seconds=int(im.shape[0]/4)))[:2][::-1]

rot = angleFromCoordinate(*bot, *top)
print(rot)

rotated_img = ndimage.rotate(im, rot)
rimg = rotated_img[:]
w = rotated_img.shape[1]
h = rotated_img.shape[0]

m = Basemap(projection='cass',lon_0 = center[1],lat_0 = center[0],width = w*4000*0.81,height = h*4000*0.81, resolution = "i")
m.drawcoastlines(color='yellow')
m.drawcountries(color='yellow')

im = plt.imshow(rotated_img, cmap='gray', extent=(*plt.xlim(), *plt.ylim()))
plt.show()
'''
plt.savefig('foo.png', bbox_inches='tight', dpi=1000)

img = misc.imread("foo.png")
img = img[100:-100,100:-100,:]
img = ndimage.rotate(img, -17)


img = misc.imresize(img, rimg.shape)

print(img.shape,oim.shape,rimg.shape)
rf = int((img.shape[0]/2) - ((img.shape[0] * oim.shape[0] / rimg.shape[0])/2))
re = int((img.shape[0]/2) + ((img.shape[0] * oim.shape[0] / rimg.shape[0])/2))
cf = int((img.shape[1]/2) - ((img.shape[1] * oim.shape[1] / rimg.shape[1])/2))
ce = int((img.shape[1]/2) + ((img.shape[1] * oim.shape[1] / rimg.shape[1])/2))
print(rf, re)
img = img[rf:re,cf:ce]

img = Image.fromarray(img[97:-97,97:-97])
img.save('my.png')
img.show()
'''