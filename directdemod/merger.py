'''
image merger
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mimg
import cartopy
import cartopy.crs as ccrs
import os
import json

from datetime import datetime, timedelta
from pyorbital.orbital import Orbital
from PIL import Image
from directdemod import constants
from directdemod.misc import Checker, compute_alt, to_datetime, extract_date, extract_coords, compute_angle
from scipy import ndimage

'''
This class provides an API for merging multiple images.
It extracts needed information and projects images on mercator
projection.
'''

class ImageMerger:

    '''
    This class provides an API for merging multiple images.
    It extracts needed information and projects images on mercator
    projection.
    '''

    def __init__(self, tle_file='', aux_file_name="temp_image_file.png"):

        '''Initialize the object

        Args:
            tle_file (:obj:`string`, optional): path to the tle file
            aux_file_name (:obj:`string`, optional): auxiliary file name
        '''

        Checker.check_libs()

        self.is_basemap = False
        self.is_cartopy = Checker.check_cartopy()
        self.tle_file   = tle_file
        self.aux_file_name = aux_file_name

    def merge_files(self, file_descriptors, whole=False, resolution=constants.RESOLUTION):

        '''merge images from image descriptors

        Args:
            file_descriptors (:obj:`list`): paths to image descriptors
            whole (:obj:`bool`, optinal): flag to generate whole image
            resolution (:obj:`int`, optional): resolution of the output image

        Returns:
            :obj:`PIL.Image`: merged image
        '''

        if file_descriptors is None:
            raise ValueError("Passed descriptors are null.")

        descriptors = [json.load(open(f)) for f in file_descriptors if Checker.is_file(f)]
        return self.merge(descriptors, whole, resolution)

    def merge(self, jsons, whole=False, resolution=constants.RESOLUTION):

        '''merge multiple images from descriptors

        Args:
            jsons (:obj:`dict`): set of dict objects, which describe images
            whole (:obj:`bool`, optinal): flag to generate whole image
            resolution (:obj:`int`, optional): resolution of the output image

        Returns:
            :obj:`PIL.Image`: merged image
        '''

        if jsons is None:
            raise ValueError("Passed objects are null.")

        projection = plt.figure()

        axes = plt.axes(projection=ccrs.PlateCarree())
        axes.coastlines(resolution='50m', color=constants.COLOR, linewidth=0.2)
        axes.add_feature(cartopy.feature.BORDERS, linestyle='-', edgecolor=constants.COLOR, linewidth=0.2)
        axes.set_extent([-180, 180, -90, 90])

        self.left_ex  = 180
        self.right_ex = -180
        self.bot_ex   = 90
        self.top_ex   = -90

        for obj in jsons:
            image, isGray = self.imread(obj["image_name"])
            center = obj["center"]
            degree = obj["direction"]

            if self.is_cartopy:
                img = self.set_transparent(ndimage.rotate(image, degree, cval=255), isGray)
                dx = img.shape[0]*4000/2*0.81 # in meters
                dy = img.shape[1]*4000/2*0.81 # in meters
                left_bot  = self.add_m(center, -1*dx, -1*dy)
                right_top = self.add_m(center, dx, dy)
                img_extent = (left_bot[1], right_top[1], left_bot[0], right_top[0])
                self.update_extents(img_extent)
                if isGray:
                    print('Gray')
                    axes.imshow(img, origin='upper', extent=img_extent, cmap='gray')
                else:
                    axes.imshow(img, origin='upper', extent=img_extent)
            elif self.is_basemap:
                raise NotImplementedError("Basemap mapping not implemented.")

        if whole:
            projection.savefig(self.aux_file_name, dpi=resolution, bbox_inches='tight')
        else:
            axes.set_extent([self.left_ex, self.right_ex, self.bot_ex, self.top_ex])
            projection.savefig(self.aux_file_name, dpi=resolution, bbox_inches='tight')

        merged = Image.open(self.aux_file_name)
        os.remove(self.aux_file_name)
        return merged

    def merge_noaa(self, objs, whole=False, resolution=constants.RESOLUTION):

        '''merge multiple noaa images from image files

        Args:
            objs (:obj:`tuple`): set of objects representing images
            whole (:obj:`bool`, optinal): flag to generate whole image
            resolution (:obj:`int`, optional): resolution of the output image

        Returns:
            :obj:`PIL.Image`: merged image
        '''

        if objs is None:
            raise ValueError("Passed objects are null.")

        descriptors = []
        for obj in objs:
            if not Checker.is_file(obj[0]):
                continue

            file_name = obj[0]
            sat_type  = obj[1]
            image     = plt.imread(file_name)

            dtime            = self.extract_date(file_name)
            top, bot, center = self.extract_coords(image, sat_type, dtime)
            degree           = self.compute_angle(*bot, *top)

            descriptor = {
                "image_name": file_name,
                "sat_type": sat_type,
                "date_time": "",
                "center": list(center),
                "direction": degree
            }

            descriptors.append(descriptor)

        return self.merge(descriptors, whole, resolution)

    def imread(self, file_name):

        '''read the image from file

        Args:
            file_name (:obj:`string`): file_name

        Returns:
            image :obj:`np.ndarray`: image with fixed transparency
            isGray :obj:`bool`: true if image is gray, false otherwise
        '''

        image = mimg.imread(file_name)
        return (image, len(image.shape) == 2)

    def set_transparent(self, image, isGray):

        '''set pixel transparency

        Args:
            image (:obj:`np.array`): image
            isGray (:obj:`bool`): flag

        Returns:
            image :obj:`np.array`: image with fixed transparency
        '''
        # Unoptimized version
        if not isGray:
            for row in image:
                for pixel in row:
                    if pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250:
                        pixel[3] = 0
            return image
        else:
            array = np.zeros((image.shape[0], image.shape[1], 4))
            for i, row in enumerate(image):
                for index, val in enumerate(row):
                    array[i][index] = np.array([val/255, val/255, val/255, (0 if val == 0 else 1)])
            return array

    def update_extents(self, extent):

        '''update bounds of the projection

        Args:
            extent (:obj:`tuple`): current image bounds
        '''

        self.left_ex  = min(self.left_ex,  extent[0])
        self.right_ex = max(self.right_ex, extent[1])
        self.bot_ex   = min(self.bot_ex,   extent[2])
        self.top_ex   = max(self.top_ex,   extent[3])

    def add_m(self, center, dx, dy):
        # source: https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters
        new_latitude  = center[0] + (dy / 6371000.0) * (180 / np.pi)
        new_longitude = center[1] + (dx / 6371000.0) * (180 / np.pi) / np.cos(center[0] * np.pi/180)
        return (new_latitude, new_longitude)

if __name__ == "__main__":
    m = ImageMerger()
