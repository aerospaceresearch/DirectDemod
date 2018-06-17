import os
import matplotlib.pyplot as plt
import numpy as np
from cartopy import config
import cartopy.crs as ccrs
from scipy import ndimage
import cartopy.feature
from scipy import misc

center = [50.521436, 6.845530]

def add_m(center, dx, dy):
	new_latitude  = center[0]  + (dy / 6371000.0) * (180 / np.pi)
	new_longitude = center[1] + (dx / 6371000.0) * (180 / np.pi) / np.cos(center[0] * np.pi/180)
	return [new_latitude, new_longitude]

fig = plt.figure()

img = plt.imread("a.png")
img = ndimage.rotate(img, -20)

dx = img.shape[0]*4000/2
dy = img.shape[1]*4000/2

dx *= 0.77
dy *= 0.77

img_extent = (add_m(center, -1*dx, -1*dy)[1], add_m(center, dx, dy)[1], add_m(center, -1*dx, -1*dy)[0], add_m(center, dx, dy)[0])

ax = plt.axes(projection=ccrs.PlateCarree())
ax.imshow(img, origin='upper', extent=img_extent, transform=ccrs.PlateCarree())
ax.coastlines(resolution='50m', color='yellow', linewidth=1)
ax.add_feature(cartopy.feature.BORDERS, linestyle='-', edgecolor='yellow')

plt.show()
