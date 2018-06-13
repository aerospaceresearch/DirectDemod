import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy import ndimage

center = [50.521436, 7.145530]

rot = -17

im = plt.imread('a.png')
rotated_img = ndimage.rotate(im, rot)
w = rotated_img.shape[1]
h = rotated_img.shape[0]

m = Basemap(projection='cass',lon_0 = center[1],lat_0 = center[0],width = w*4000*0.8,height = h*4000*0.8, resolution = "i")
m.drawcoastlines(color='yellow')
m.drawcountries(color='yellow')

im = plt.imshow(rotated_img, extent=(*plt.xlim(), *plt.ylim()))
plt.show()