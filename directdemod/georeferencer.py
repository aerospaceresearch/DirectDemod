"""
This module provides an API for image georeferencing,
map overlay, tif to png conversion and others.
It extracts the information from descriptor file and
warps the image to defined projection.
"""

import argparse
import json
import os

from shutil import copyfile
from datetime import timedelta
from typing import List

import dateutil.parser as dparser
import matplotlib.image as mimg
import numpy as np
import tifffile

from PIL import Image
from osgeo import gdal
from osgeo.gdal import GRA_NearestNeighbour, GRA_Bilinear, GRA_Cubic
from geographiclib.geodesic import Geodesic
from pyorbital.orbital import Orbital
from directdemod import constants
from directdemod.misc import Encoder


class Georeferencer(object):
    """
    This class provides an API for image georeferencing.
    It extracts the information from descriptor file, translates
    and warps the image to defined projection.
    """

    def __init__(self, tle_file: str = ""):
        """Georeferencer constructor

        Args:
            tle_file (:obj:`string`, optional): file with orbit parameters

        """

        self.tle_file = tle_file

    def georef_tif(self,
                   image_name: str,
                   output_file: str,
                   resample_alg=GRA_NearestNeighbour) -> None:
        """georeferences the satellite image from tif file using GDAL
        Python API. Descriptor is extracted directly from tif file

        Args:
            image_name (:obj:`string`): path to tiff file, which contains needed metadata
            output_file (:obj:`string`): path to output file
            resample_alg (:obj:`gdalconst`): resampling algorithm (nearest, bilinear, cubic)
        """

        with tifffile.TiffFile(image_name) as tif:
            page = tif.pages[0]
            descriptor = page.tags["ImageDescription"].value

        descriptor = json.loads(descriptor)

        self.georef(descriptor, output_file, resample_alg)

    def georef(self,
               descriptor: dict,
               output_file: str,
               resample_alg=GRA_NearestNeighbour) -> None:
        """georeferences the satellite image from descriptor file using GDAL
        Python API

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
            resample_alg (:obj:`gdalconst`, optional): algorithm for resampling
        """

        file_name = descriptor["image_name"]
        image = mimg.imread(file_name)

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
                                   resampleAlg=resample_alg)

        gdal.Warp(destNameOrDestDS=output_file,
                  srcDSOrSrcDSTab=constants.TEMP_TIFF_FILE,
                  options=options)

        os.remove(constants.TEMP_TIFF_FILE)

    def georef_os(self, descriptor: dict, output_file: str) -> None:
        """georeferences the satellite image from descriptor file, using GDAL
        compiled binaries. Can be used when gdal binaries are available only

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        """

        file_name = descriptor["image_name"]
        image = mimg.imread(file_name)

        gcps = self.compute_gcps(descriptor, image)

        translate_flags = "-of GTiff -a_srs EPSG:4326"
        warp_flags = "-r near -tps -s_srs EPSG:4326 -t_srs EPSG:4326"

        translate_query = 'gdal_translate ' + translate_flags + ' ' + self.to_string_gcps(gcps) \
                          + ' "' + file_name + '" ' + ' "' + constants.TEMP_TIFF_FILE + '"'

        warp_query = 'gdalwarp ' + warp_flags + ' "' + constants.TEMP_TIFF_FILE + '" ' + ' "' + output_file + '"'

        os.system(translate_query)
        os.system(warp_query)

        os.remove(constants.TEMP_TIFF_FILE)

    @staticmethod
    def to_string_gcps(gcps: List[gdal.GCP]) -> str:
        """create string representation of gcp points

        Args:
            gcps (:obj:`list`): list of gcp points

        Returns:
            :obj:`string`: gcp points represented as a string
        """

        return " ".join([
            ("-gcp " + str(gcp.GCPPixel) + " " + str(gcp.GCPLine) + " " +
             str(gcp.GCPX) + " " + str(gcp.GCPY)) for gcp in gcps
        ])

    @staticmethod
    def create_desc(descriptor: dict, output_file: str) -> None:
        """create descriptor for `output_file` file

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        """

        desc = {
            "image_name": output_file,
            "sat_type": descriptor["sat_type"],
            "date_time": descriptor["date_time"],
            "center": descriptor["center"],
            "direction": descriptor["direction"]
        }

        name, _ = os.path.splitext(output_file)
        desc_name = name + "_desc.json"
        json.dump(desc, open(desc_name, 'w'), cls=Encoder)

    def compute_gcps(self, descriptor: dict,
                     image: np.ndarray) -> List[gdal.GCP]:
        """compute set of Ground Control Points

        Args:
            descriptor (:obj:`dict`): descriptor dictionary, which describes the image
            image (:obj:`np.ndarray`): image as np.ndarray

        Returns:
            :obj:`list`: list of GCPs
        """

        height = image.shape[0]
        width = image.shape[1]
        center_w = width / 2

        gcps = []
        dtime = dparser.parse(descriptor["date_time"]) - timedelta(seconds=180)
        orbiter = Orbital(descriptor["sat_type"], tle_file=self.tle_file)
        min_delta = 500
        middle_dist = 3.25 * 455 / 2. * 1000
        far_dist = 3.15 * 455 * 1000  # 3.15 is because of image distortions towards to boudaries
        prev_position = orbiter.get_lonlatalt(dtime - timedelta(
            milliseconds=min_delta * 10))

        for i in range(0, height, 10):
            current_height = height - i - 1
            gcp_time = dtime + timedelta(milliseconds=i * min_delta)
            position = orbiter.get_lonlatalt(gcp_time)
            gcps.append(
                gdal.GCP(position[0], position[1], 0, center_w,
                         current_height))

        for i in range(0, height, 100):
            current_height = height - i - 1
            gcp_time = dtime + timedelta(milliseconds=i * min_delta)
            position = orbiter.get_lonlatalt(gcp_time)

            angle = self.compute_angle(prev_position[0], prev_position[1],
                                       position[0], position[1])
            azimuth = 90 - angle

            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth,
                                 middle_dist, 3 * width / 4, current_height))
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth, far_dist,
                                 width, current_height))

            # Note +2 degrees is hand constant
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth + 182,
                                 middle_dist, width / 4, current_height))
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth + 182,
                                 far_dist, 0, current_height))

            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth,
                                 middle_dist / 2, 5 * width / 8,
                                 current_height))
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth,
                                 3 * middle_dist / 2, 7 * width / 8,
                                 current_height))

            # Note +2 degrees is hand constant
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth + 182,
                                 middle_dist / 2, 3 * width / 8,
                                 current_height))
            gcps.append(
                self.compute_gcp(position[0], position[1], azimuth + 182,
                                 3 * middle_dist / 2, width / 8,
                                 current_height))

            prev_position = position

        return gcps

    @staticmethod
    def compute_gcp(long: float, lat: float, angle: float, distance: float,
                    width: float, height: float) -> gdal.GCP:
        """compute coordinate of GCP, using longitude and latitude of starting point,
        azimuth angle and distance to the point

        Args:
            long (:obj:`float`): longitude of start point
            lat (:obj:`float`): latitude of start point
            angle (:obj:`float`): azimuth between start point and GCP
            distance (:obj: `float`): distance to point in meters
            width (:obj:`float`): w-axis coordinate
            height (:obj:`float`): height-axis coordinate

        Returns:
            :obj:`gdal.GCP`: instance of GCP object
        """

        coords = Geodesic.WGS84.Direct(lat, long, angle, distance)
        return gdal.GCP(coords['lon2'], coords['lat2'], 0, width, height)

    @staticmethod
    def compute_angle(long1: float, lat1: float, long2: float,
                      lat2: float) -> float:
        """compute angle between 2 points, defined by latitude and longitude

        Args:
            long1 (:obj:`float`): longitude of start point
            lat1 (:obj:`float`): latitude of start point
            long2 (:obj:`float`): longitude of end point
            lat2 (:obj:`float`): latitude of end point

        Returns:
            :obj:`float`: angle between points
        """

        lat1 = np.radians(lat1)
        long1 = np.radians(long1)
        lat2 = np.radians(lat2)
        long2 = np.radians(long2)

        d_lon = (long2 - long1)

        sincos = np.sin(d_lon) * np.cos(lat2)
        cosdiff = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(
            lat2) * np.cos(d_lon)
        brng = np.arctan2(sincos, cosdiff)
        brng = np.degrees(brng)
        brng = (brng + 360) % 360
        brng = 360 - brng
        return brng


def overlay(raster_path: str,
            shapefile: str = constants.BORDERS,
            grayscale: bool = True) -> None:
    """create map overlay of borders shape file over raster

    Args:
        raster_path (:obj:`string`): path to raster (.tif)
        shapefile (:obj:`string`): path to shape file (.shp)
        grayscale (:obj:`bool`): type of image

    Throws:
        :obj:`NotImplementedError`: if passed grayscale False
    """

    if grayscale:
        vector_ds = gdal.OpenEx(shapefile, gdal.OF_VECTOR)
        raster_ds = gdal.Open(raster_path, gdal.GA_Update)
        gdal.Rasterize(raster_ds, vector_ds, bands=[1], burnValues=[255])
    else:
        raise NotImplementedError()


def tif_to_png(filename: str, png_file: str, grayscale: bool = True) -> None:
    """covert tif image to png

    Args:
        filename (:obj:`string`): path to image (.tif)
        png_file (:obj:`string`): name of output file (.png)
        grayscale (:obj:`bool`): type of image

    Throws:
        :obj:`NotImplementedError`: if passed grayscale False
    """

    if grayscale:
        img = Image.open(filename).convert("LA")
        img.save(png_file)
    else:
        raise NotImplementedError


def set_nodata(filename: str, value: int = 0) -> None:
    """sets no-data value of tif 'filename' to 'value'

    Args:
        filename (:obj:`string`): path to image (.tif)
        value (:obj:`int`): value to set as no-data value
    """

    _set_nodata(filename, constants.TEMP_TIFF_FILE, value=value)
    os.remove(filename)
    copyfile(constants.TEMP_TIFF_FILE, filename)
    os.remove(constants.TEMP_TIFF_FILE)


def _set_nodata(filename: str, output_file: str, value: int = 0) -> None:
    """sets no-data value of tif 'filename' to 'value', saves to output_file

    Args:
        filename (:obj:`string`): path to image (.tif)
        output_file (:obj:`string`): name of output file (.tif)
        value (:obj:`int`): value to set as no-data value
    """

    options = gdal.TranslateOptions(format="GTiff", noData=value)

    gdal.Translate(destName=output_file, srcDS=filename, options=options)


def main() -> None:
    """Georeferencer CLI interface"""

    parser = argparse.ArgumentParser(description="Noaa georeferencer.")
    parser.add_argument('-i', '--image_name', required=True)
    parser.add_argument('-o', '--output_file', required=False)
    parser.add_argument('-m', '--map', action='store_true')
    parser.add_argument('-r', '--resample', required=False)

    args = parser.parse_args()

    resample = args.resample
    if resample is None or resample == 'nearest':
        resample = GRA_NearestNeighbour
    elif resample == 'bilinear':
        resample = GRA_Bilinear
    elif resample == 'cubic':
        resample = GRA_Cubic
    else:
        raise ValueError(
            "ERROR: Invalid resample algorithm (nearest, bilinear, cubic): " +
            str(resample))

    referencer = Georeferencer(tle_file=constants.TLE_NOAA)
    output_file = args.output_file if args.output_file is not None else args.image_name

    referencer.georef_tif(args.image_name, output_file, resample_alg=resample)

    if args.map:
        overlay(output_file)


if __name__ == "__main__":
    main()
