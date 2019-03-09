'''
image merger
'''
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import os
import config

from datetime import datetime, timedelta
from pyorbital.orbital import Orbital
from PIL import Image
from lib_checker import Checker
from scipy import ndimage

'''
This class provides an API for merging multiple images.
It extracts needed information and projects images on mercator
projection.
'''

class ImageMerger:

    '''
    Class for merging multiple images
    '''

    def __init__(self, tle_file, resolution=config.RESOLUTION, aux_file_name="temp_image_file.png"):

        '''Initialize the object

        Args:
            tle_file (:obj:`string`): path to the tle file
            resolution (:obj:`int`, optional): resolution of the output image
            aux_file_name (:obj:`string`, optional): auxiliary file name
        '''

        Checker.check_libs()

        self.is_basemap = Checker.check_basemap()
        self.is_cartopy = Checker.check_cartopy()
        self.resolution = resolution
        self.tle_file   = tle_file
        self.aux_file_name = aux_file_name

    def merge_images(self, objs, whole=False):

        '''Merge multiple images

        Args:
            objs (:obj:`tuple(np.array, tuple(float, float), float)`): set of objects representing images
            whole (:obj:`bool`, optinal): flag to generate whole image

        Returns:
            :obj:`PIL.Image`: merged image
        '''

        if objs is None:
            raise ValueError("Passed objects are null.")

        projection = plt.figure()

        axes = plt.axes(projection=ccrs.PlateCarree())
        axes.coastlines(resolution='50m', color=config.COLOR, linewidth=0.2)
        axes.add_feature(cartopy.feature.BORDERS, linestyle='-', edgecolor=config.COLOR, linewidth=0.2)
        axes.set_extent([-180, 180, -90, 90])

        self.left_ex  = 180
        self.right_ex = -180
        self.bot_ex   = 90
        self.top_ex   = -90

        for obj in objs:
            image  = obj[0]
            center = obj[1]
            degree = obj[2]

            if self.is_cartopy:
                img = ndimage.rotate(image, degree - 180, cval=255)
                dx = img.shape[0]*4000/2*0.81 # in meters
                dy = img.shape[1]*4000/2*0.81 # in meters
                left_bot  = self.add_m(center, -1*dx, -1*dy)
                right_top = self.add_m(center, dx, dy)
                img_extent = (left_bot[1], right_top[1], left_bot[0], right_top[0])
                self.update_extents(img_extent)
                axes.imshow(img, origin='upper', extent=img_extent)
            elif self.is_basemap:
                raise NotImplementedError("Basemap mapping not implemented.")

        if whole:
            projection.savefig(self.aux_file_name, dpi=self.resolution, bbox_inches='tight')
        else:
            axes.set_extent([self.left_ex, self.right_ex, self.bot_ex, self.top_ex])
            projection.savefig(self.aux_file_name, dpi=self.resolution, bbox_inches='tight')

        merged = Image.open(self.aux_file_name)
        os.remove(self.aux_file_name)
        return merged

    def merge_from_files(self, objs, whole=False):

        '''Merge multiple images from files

        Args:
            objs (:obj:`tuple(string, string)`): set of objects representing images
            whole (:obj:`bool`, optinal): flag to generate whole image

        Returns:
            :obj:`PIL.Image`: merged image
        '''

        if objs is None:
            raise ValueError("Passed objects are null.")

        image_objects = []
        for obj in objs:
            if not Checker.is_file(obj[0]):
                continue

            file_name = obj[0]
            sat_type  = obj[1]
            image     = plt.imread(file_name)

            dtime            = self.extract_date(file_name)
            top, bot, center = self.extract_coords(image, sat_type, dtime)
            degree           = self.compute_angle(*bot, *top)

            image_objects.append((image, center, degree))

        return self.merge_images(image_objects, whole)

    def update_extents(self, extent):

        '''Update bounds of the projection

        Args:
            extent (:obj:`tuple(float, float, float, float)`): current image bounds
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

    @staticmethod
    def extract_date(filename):

        '''Extracts date from filename

        Args:
            filename (:obj:`string`): name of the file

        Returns:
            :obj:`datetime`: contructed datetime object
        '''

        parts = filename.split('_')
        image_date, image_time = None, None
        for index, part in reversed(list(enumerate(parts))):
            if part[-1] == "Z":
                image_time = part[:-1]
                image_date = parts[index - 1]

        if image_date is None or image_time is None:
            raise ValueError("Invalid file name format.")

        return ImageMerger.to_datetime(image_time, image_date)

    @staticmethod
    def to_datetime(image_time, image_date):

        '''Builds datetime object

        Args:
            image_time (:obj:`string`): time when the image was captured
            image_date (:obj:`string`): date when the image was captured

        Returns:
            :obj:`datetime`: contructed datetime object
        '''

        try:
            year   = int(image_date[0:4])
            month  = int(image_date[4:6])
            day    = int(image_date[6:8])
            hour   = int(image_time[0:2])
            minute = int(image_time[2:4])
            second = int(image_time[4:6])

            return datetime(year, month, day, hour, minute, second)
        except ValueError as e:
            # add error logging
            raise

    def extract_coords(self, image, satellite, dtime):

        '''Extracts coordinates of the image bounds

        Args
            image (:obj:`np.array`): captured image
            satellite (:obj:`string`): name of the satellite
            dtime (:obj:`datetime`): time when the image was captured

        Returns:
            :obj:`tuple`: extracted coordinates
        '''

        orbiter = Orbital(satellite) if self.tle_file is None else Orbital(satellite, tle_file=self.tle_file)
        delta = int(image.shape[0]/16)
        delta = max(delta, 10)

        top_coord    = self.compute_alt(orbiter, dtime, image, -delta)
        bot_coord    = self.compute_alt(orbiter, dtime, image,  delta)
        center_coord = self.compute_alt(orbiter, dtime, image, 0)

        return (top_coord, bot_coord, center_coord)

    def compute_alt(self, orbiter, dtime, image, accumulate):

        '''Compute coordinates of the satellite

        Args
            orbiter (:obj:`Orbital`): object for orbit calculation
            dtime (:obj:`datetime`): time when the image was captured
            image (:obj:`np.array`): capturedimage
            accumulate (:obj:`float`): distance shift

        Returns:
            :obj:`tuple`: coordinates of satellite at certain point of time
        '''

        return orbiter.get_lonlatalt(dtime + timedelta(seconds=int(image.shape[0]/4) + accumulate))[:2][::-1]

    def compute_angle(self, lat1, long1, lat2, long2):
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
