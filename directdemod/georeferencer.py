'''
image georeferencer
'''
import dateutil.parser as dparser
import matplotlib.image as mimg
import numpy as np
import constants
import math
import os

from osgeo import gdal
from osgeo.gdal import GRA_NearestNeighbour
from geographiclib.geodesic import Geodesic
from datetime import datetime, timedelta
from pyorbital.orbital import Orbital
from json_parser import JsonParser

'''
This class provides an API for image georeferencing.
It extracts the infromation from descriptor file and
warps the image to defined projection.
'''

class Georeferencer:

    '''
    Class for georeferencing
    '''

    def __init__(self, tle_file=""):

        '''Georeferencer constructor

        Args:
            tle_file (:obj:`string`): file with orbit parameters

        '''

        self.tle_file = tle_file

    def georef(self, descriptor, output_file, desc=False):

        '''Main georeferencing routine

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
            desc (:obj:`bool`): descriptor flag
        '''

        file_name = descriptor["image_name"]
        image     = mimg.imread(file_name)

        gcps = self.compute_gcps(descriptor, image)

        options = gdal.TranslateOptions(format="GTiff",
                                        outputSRS=constants.DEFAULT_RS,
                                        GCPs=gcps)

        gdal.Translate(destName=constants.TEMP_TIFF_FILE,
                        srcDS=file_name,
                        options=options)

        options = gdal.WarpOptions(srcSRS=constants.DEFAULT_RS,
                                    dstSRS=constants.DEFAULT_RS,
                                    tps=True,
                                    resampleAlg=GRA_NearestNeighbour)

        gdal.Warp(destNameOrDestDS=output_file,
                    srcDSOrSrcDSTab=constants.TEMP_TIFF_FILE,
                    options=options)

        os.remove(constants.TEMP_TIFF_FILE)

        if desc:
            self.create_desc(descriptor, output_file)

    def georef_os(self, descriptor, output_file, desc=False):

        '''Main georeferencing routine

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
            desc (:obj:`bool`): descriptor flag
        '''

        file_name = descriptor["image_name"]
        image     = mimg.imread(file_name)

        gcps = self.compute_gcps(descriptor, image)

        translate_flags = "-of GTiff -a_srs EPSG:4326"
        warp_flags = "-r near -tps -s_srs EPSG:4326 -t_srs EPSG:4326"

        translate_query = 'gdal_translate ' + translate_flags + ' ' + self.to_string_gcps(gcps) + ' "' + file_name + '" ' + ' "' + constants.TEMP_TIFF_FILE + '"'
        warp_query = 'gdalwarp ' + warp_flags + ' "' + constants.TEMP_TIFF_FILE + '" ' + ' "' + output_file + '"'

        os.system(translate_query)
        os.system(warp_query)

        os.remove(constants.TEMP_TIFF_FILE)

        if desc:
            self.create_desc(descriptor, output_file)

    def to_string_gcps(self, gcps):
        return " ".join([("-gcp " + str(gcp.GCPPixel) + " " + str(gcp.GCPLine) + " " + str(gcp.GCPX) + " " + str(gcp.GCPY)) for gcp in gcps])


    def create_desc(self, descriptor, output_file):

        '''Create descriptor file

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        '''

        desc = {
            "image_name": output_file,
            "sat_type": descriptor["sat_type"],
            "date_time": descriptor["date_time"],
            "center": descriptor["center"],
            "direction": 0
        }

        name, extension = os.path.splitext(output_file)
        desc_name = name + "_desc.json"
        JsonParser.save(desc, desc_name)

    def compute_gcps(self, descriptor, image):
        height = image.shape[0]
        width  = image.shape[1]
        center_w = width/2
        center_h = height/2

        gcps = []
        dtime = dparser.parse(descriptor["date_time"])
        orbiter = Orbital(descriptor["sat_type"], tle_file=self.tle_file)
        min_delta = 500
        middle_dist = 3.22 * 455 / 2. * 1000
        far_dist = 3.2 * 455 * 1000
        prev = orbiter.get_lonlatalt(dtime - timedelta(milliseconds=min_delta*10))

        for i in range(0, height, 100):
            h = height - i - 1
            gcp_time = dtime + timedelta(milliseconds=i*min_delta)
            position = orbiter.get_lonlatalt(gcp_time)
            gcps.append(gdal.GCP(position[0], position[1], 0, center_w, h))

            angle = self.angleFromCoordinate(prev[0], prev[1], position[0], position[1])
            azimuth = 90 - angle

            gcps.append(self.compute_gcp(position[0], position[1], azimuth, middle_dist, 3*width/4, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth, far_dist, width, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 183, middle_dist, width/4, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 183, far_dist, 0, h)) # FIXME: Note +3 degrees is hand constant

            prev = position

        return gcps

    def compute_gcp(self, long, lat, angle, distance, w, h):

        '''Compute single GCP

        Args:
            h (:obj:`float`): h-axis coordinate
            w (:obj:`float`): w-axis coordinate
            angle (:obj:`float`): azimuth of point
        '''

        coords = Geodesic.WGS84.Direct(lat, long, angle, distance)
        return gdal.GCP(coords['lon2'], coords['lat2'], 0, w, h)

    def angleFromCoordinate(self, long1, lat1, long2, lat2):
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

if __name__ == "__main__":
    file_name = "../samples/image_noaa19_1_desc.json"
    output_file = "../samples/image_noaa19_2.tif"
    descriptor = JsonParser.from_file(file_name)

    referencer = Georeferencer(tle_file="../tle/noaa18_June_14_2018.txt")
    referencer.georef(descriptor, output_file)
