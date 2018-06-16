import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy import ndimage

center = [39.802613264377825, -14.536830769290223]
center = [53.5480150544989, -20.38914395572289]
center = [ 51.86099209979376,15.925813399768762]
center = [6.859298612741445, 64.77839469486523][::-1]
rot = +17+180

im = plt.imread('d.png')
#im = im[:,1040:]
print(im.shape)
rotated_img = ndimage.rotate(im, rot)
w = rotated_img.shape[1]
h = rotated_img.shape[0]

m = Basemap(projection='cass',lon_0 = center[1],lat_0 = center[0],width = w*4000*0.8,height = h*4000*0.8, resolution = "i")
m.drawcoastlines(color='yellow')
m.drawcountries(color='yellow')

im = plt.imshow(rotated_img, extent=(*plt.xlim(), *plt.ylim()))
plt.show()