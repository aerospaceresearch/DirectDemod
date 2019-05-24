'''
image georeferencer
'''
import dateutil.parser as dparser
import matplotlib.image as mimg
import numpy as np
import argparse
import math
import os

from PIL import Image
from osgeo import gdal
from osgeo.gdal import GRA_NearestNeighbour
from geographiclib.geodesic import Geodesic
from datetime import datetime, timedelta
from pyorbital.orbital import Orbital
from directdemod import constants
from directdemod.misc import JsonParser

'''
This class provides an API for image georeferencing.
It extracts the information from descriptor file and
warps the image to defined projection.
'''

class Georeferencer:

    '''
    This class provides an API for image georeferencing.
    It extracts the information from descriptor file, translates
    and warps the image to defined projection.
    '''

    def __init__(self, tle_file=""):

        '''Georeferencer constructor

        Args:
            tle_file (:obj:`string`, optional): file with orbit parameters

        '''

        self.tle_file = tle_file

    def georef(self, descriptor, output_file, desc=False):

        '''georeferences the satellite image from descriptor file using GDAL
        Python API

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
            desc (:obj:`bool`, optional): descriptor flag, true if descriptor should be generated
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

        '''georeferences the satellite image from descriptor file, using GDAL
        compiled binaries

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
            desc (:obj:`bool`): descriptor flag, true if descriptor should be generated
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

        '''create string representation of gcp points

        Args:
            gcps (:obj:`list`): list of gcp points

        Returns:
            :obj:`string`: gcp points represented as a string
        '''

        return " ".join([("-gcp " + str(gcp.GCPPixel) + " " + str(gcp.GCPLine) + " " + str(gcp.GCPX) + " " + str(gcp.GCPY)) for gcp in gcps])


    def create_desc(self, descriptor, output_file):

        '''create descriptor file

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        '''

        desc = {
            "image_name": output_file,
            "sat_type": descriptor["sat_type"],
            "date_time": descriptor["date_time"],
            "center": descriptor["center"],
            "direction": descriptor["direction"]
        }

        name, extension = os.path.splitext(output_file)
        desc_name = name + "_desc.json"
        JsonParser.save(desc, desc_name)

    def compute_gcps(self, descriptor, image):

        '''compute set of Ground Control Points

        Args:
            h (:obj:`dict`): descriptor dictionary, which describes the image
            w (:obj:`np.ndarray`): image as np.ndarray

        Returns:
            :obj:`list`: list of GCPs
        '''

        height = image.shape[0]
        width  = image.shape[1]
        center_w = width/2
        center_h = height/2

        gcps = []
        dtime = dparser.parse(descriptor["date_time"])-timedelta(seconds=180) # start capture date in 2s (it is hands-on parameter)
        orbiter = Orbital(descriptor["sat_type"], tle_file=self.tle_file)
        min_delta = 500
        middle_dist = 3.25 * 455 / 2. * 1000
        far_dist = 3.15 * 455 * 1000 # 3.15 is because of image distortions towards to boudaries
        prev_position = orbiter.get_lonlatalt(dtime - timedelta(milliseconds=min_delta*10))

        for i in range(0, height, 10):
            h = height - i - 1
            gcp_time = dtime + timedelta(milliseconds=i*min_delta)
            position = orbiter.get_lonlatalt(gcp_time)
            gcps.append(gdal.GCP(position[0], position[1], 0, center_w, h))

        for i in range(0, height, 100):
            h = height - i - 1
            gcp_time = dtime + timedelta(milliseconds=i*min_delta)
            position = orbiter.get_lonlatalt(gcp_time)

            angle = self.angleFromCoordinate(prev_position[0], prev_position[1], position[0], position[1])
            azimuth = 90 - angle

            gcps.append(self.compute_gcp(position[0], position[1], azimuth, middle_dist, 3*width/4, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth, far_dist, width, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 182, middle_dist, width/4, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 182, far_dist, 0, h)) # FIXME: Note +2 degrees is hand constant

            gcps.append(self.compute_gcp(position[0], position[1], azimuth, middle_dist/2, 5*width/8, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth, 3*middle_dist/2, 7*width/8, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 182, middle_dist/2, 3*width/8, h))
            gcps.append(self.compute_gcp(position[0], position[1], azimuth + 182, 3*middle_dist/2, width/8, h))

            prev_position = position

        return gcps

    def compute_gcp(self, long, lat, angle, distance, w, h):

        '''compute coordinate of GCP, using longitude and latitude of starting point,
        azimuth angle and distance to the point

        Args:
            long (:obj:`float`): longitude of start point
            lat (:obj:`float`): latitude of start point
            angle (:obj:`float`): azimuth between start point and GCP
            h (:obj:`float`): h-axis coordinate
            w (:obj:`float`): w-axis coordinate

        Returns:
            :obj:`gdal.GCP`: instance of GCP object
        '''

        coords = Geodesic.WGS84.Direct(lat, long, angle, distance)
        return gdal.GCP(coords['lon2'], coords['lat2'], 0, w, h)

    def angleFromCoordinate(self, long1, lat1, long2, lat2):

        '''compute angle between 2 points, defined by latitude and longitude

        Args:
            long1 (:obj:`float`): longitude of start point
            lat1 (:obj:`float`): latitude of start point
            long2 (:obj:`float`): longitude of end point
            lat2 (:obj:`float`): latitude of end point

        Returns:
            :obj:`float`: angle between points
        '''

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

def overlay(raster_path, shapefile=constants.BORDERS):

    '''create map overlay of borders shape file over raster

        Args:
            raster_path (:obj:`string`): path to raster (.tif)
            shapefile (:obj:`string`): path to shape file (.shp)
    '''

    vector_ds = gdal.OpenEx(shapefile, gdal.OF_VECTOR)
    ds = gdal.Open(raster_path, gdal.GA_Update)
    gdal.Rasterize(ds, vector_ds, bands=[1], burnValues=[255])

def tif_to_png(filename, png, grayscale=True):

    '''covert tif image to png

        Args:
            filename (:obj:`string`): path to image (.tif)
            png (:obj:`string`): name of output file (.png)

        Throws:
            error (:obj:`NotImplementedError`): if passed grayscale False
    '''

    if grayscale:
        img = Image.open(filename).convert("LA")
        img.save(png)
    else:
        raise NotImplementedError;

def main():
    '''Georeferencer CLI interface'''

    parser = argparse.ArgumentParser(description="Noaa georeferencer.")
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-m', '--map', required=False, nargs='?', const=True, type=bool)

    args = parser.parse_args()

    descriptor = JsonParser.from_file(args.file)

    referencer = Georeferencer(tle_file=constants.TLE_NOAA)
    referencer.georef(descriptor, args.output_file)

    if args.map is not None:
        overlay(args.output_file)

if __name__ == "__main__":
    main()
