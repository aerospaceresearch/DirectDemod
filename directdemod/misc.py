'''
library checker
'''
import os.path
import json
import urllib
import argparse
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from pyorbital.orbital import Orbital
from directdemod import constants

'''
The class provides functionality to determine whether all needed
libraries are installed and functional.
'''

class Checker:

    '''
    The class provides functionality to determine whether all needed
    libraries are installed and functional.
    '''

    @staticmethod
    def is_file(filename):

        '''check if given path is a file

        Args:
            filename (:obj:`string`): path

        Returns:
            :obj:`bool`: true if file, else otherwise
        '''

        return os.path.isfile(filename)

    @staticmethod
    def is_dir(dirname):

        '''check if given path is directory

        Args:
            dirname (:obj:`string`): path

        Returns:
            :obj:`bool`: true directory, else otherwise
        '''

        return os.path.isdir(filename)

    @staticmethod
    def check_libs():

        '''check if pyorbital and (cartopy or basemap) are installed

        Throws:
            :obj:`ModuleNotFoundError`: if module is not installed
        '''

        if not Checker.check_pyorbital():
            raise ModuleNotFoundError("Pyorbital must be installed.")

        if not Checker.check_cartopy() and not Checker.check_basemap():
            raise ModuleNotFoundError("Cartopy or Basemap must be installed.")

    @staticmethod
    def check_pyorbital():

        '''check if pyorbital is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import pyorbital
            from pyorbital import tlefile
            from pyorbital.orbital import Orbital
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_cartopy():

        '''check if cartopy is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import cartopy
            import cartopy.crs
            import cartopy.feature
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_basemap():

        '''check if basemap is installed

        Returns:
            :obj:`bool`: true if installed, false otherwise
        '''

        try:
            import mpl_toolkits.basemap
            from mpl_toolkits.basemap import Basemap
            return True
        except Error as e:
            return False

    @staticmethod
    def check_gdal():
        '''check if basemap is installed

        Returns:
            :obj:`
            bool`: true if installed, false otherwise
        '''

        try:
            from osgeo import gdal
            return True
        except Error as e:
            return False

'''
Object for json manipulation
'''

'''
These classes provide API for the input/output operations
with json files.
'''

class Encoder(json.JSONEncoder):

    '''
    JSON encoder
    '''

    def default(self, obj):

        '''Encode the object

        Args:
            obj (:obj:`object`): oject to encode

        Returns:
            :obj:`object`: encoded object
        '''

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super.default(self, obj)

class JsonParser:

    '''
    Wrapper class over json module to add numpy and datetime json serialization
    '''

    @staticmethod
    def to_string(json_dict):

        '''convert dict to json string

        Args:
            json_dict (:obj:`dict`): object to convert

        Returns:
            :obj:`string`: json string
        '''

        return json.dumps(json_dict, cls=Encoder)

    @staticmethod
    def from_string(str):

        '''convert json string to dict

        Args:
            str (:obj:`string`): string to convert

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.loads(str)

    @staticmethod
    def from_file(filename):

        '''convert text from file into json dict

        Args:
            filename (:obj:`string`): path to file

        Returns:
            :obj:`dict`: json dictionary
        '''

        with open(filename, 'r') as f:
            return json.load(f)

    @staticmethod
    def from_url(url):

        '''convert text from url into json dict

        Args:
            filename (:obj:`string`): path to url

        Returns:
            :obj:`dict`: json dictionary
        '''

        return json.load(urllib.urlopen(url))

    @staticmethod
    def save(json_dict, output_file):

        '''serialize json dict into file

        Args:
            json_dict (:obj:`dict`): dictionary
            output_file (:obj:`string`): path to file
        '''

        with open(output_file, 'w') as out:
            json.dump(json_dict, out, cls=Encoder)


def to_datetime(image_time, image_date):

    '''builds datetime object

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

def compute_alt(orbiter, dtime, image, accumulate):

    '''compute coordinates of the satellite

    Args:
        orbiter (:obj:`Orbital`): object representing orbit of satellite
        dtime (:obj:`datetime`): time when the image was captured
        image (:obj:`np.array`): captured image
        accumulate (:obj:`float`): distance shift

    Returns:
        :obj:`tuple`: coordinates of satellite at certain point of time
    '''

    return orbiter.get_lonlatalt(dtime + timedelta(seconds=int(image.shape[0]/4) + accumulate))[:2][::-1]


def extract_date(filename):

    '''extracts date from filename

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

    return to_datetime(image_time, image_date)

def extract_coords(image, satellite, dtime, tle_file=None):

    '''extracts coordinates of the image bounds

    Args:
        image (:obj:`np.array`): captured image
        satellite (:obj:`string`): name of the satellite
        dtime (:obj:`datetime`): time when the image was captured

    Returns:
        :obj:`tuple`: extracted coordinates
    '''

    orbiter = Orbital(satellite) if tle_file is None else Orbital(satellite, tle_file=tle_file)
    delta = int(image.shape[0]/16)
    delta = max(delta, 10)

    top_coord    = compute_alt(orbiter, dtime, image, -delta)
    bot_coord    = compute_alt(orbiter, dtime, image,  delta)
    center_coord = compute_alt(orbiter, dtime, image, 0)

    return (top_coord, bot_coord, center_coord)

def compute_angle(lat1, long1, lat2, long2):

    '''compute angle between 2 points, defined by latitude and longitude

    Args:
        lat1 (:obj:`float`): latitude of start point
        long1 (:obj:`float`): longitude of start point
        lat2 (:obj:`float`): latitude of end point
        long2 (:obj:`float`): longitude of end point

    Returns:
        :obj:`float`: angle between points
    '''

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

def create_desc(file_name, image_name, output_file="", sat_type="NOAA 19", tle_file=None):

    '''create descriptor file for audio record

    Args:
        file_name (:obj:`string`): path to audio record
        output_file (:obj:`string`): output file name
        image_name (:obj:`string`): path to image file
        sat_type (:obj:`string`): name of the satellite
        tle_file (:obj:`string`): path to tle file
    '''

    name, ext = os.path.splitext(file_name)
    desc_name = name + "_desc.json"
    image = plt.imread(image_name)

    dtime            = extract_date(file_name)
    top, bot, center = extract_coords(image, sat_type, dtime, tle_file=tle_file)
    degree           = compute_angle(*bot, *top)

    descriptor = {
        "image_name": os.path.abspath(image_name),
        "sat_type": sat_type,
        "date_time": dtime,
        "center": list(center),
        "direction": degree
    }

    if output_file:
        JsonParser.save(descriptor, output_file)
    else:
        JsonParser.save(descriptor, desc_name)

def main():
    '''Descriptor CLI interface'''
    parser = argparse.ArgumentParser(description="Create descriptor file from SDR")
    parser.add_argument('-f', '--file_sdr', required=True, help='Path to SDR recording file.')
    parser.add_argument('-i', '--image_name', required=True, help='Path to decoded image.')
    parser.add_argument('-o', '--output_file', required=False, help='Name of output file.', default="")
    parser.add_argument('-t', '--tle', required=False, help='Path to tle file.')
    parser.add_argument('-s', '--sat_type', required=False, help='Satellite type. \'NOAA 19\' by default.', default="NOAA 19")

    args = parser.parse_args()

    filename    = args.file_sdr
    image_name  = args.image_name
    output_file = args.output_file
    sat_type    = args.sat_type

    allowed_sats = ['NOAA 18', 'NOAA 19', 'NOAA 15']

    if sat_type not in allowed_sats:
        raise ValueError('Invalid satellite type: {0}'.format(sat_type))

    tle_file = args.tle

    if tle_file is None:
        tle_file = constants.TLE_NOAA

    create_desc(filename, image_name, output_file, sat_type, tle_file)

# Example arguments
# -f = "../samples/SDRSharp_20190521_152538Z_137500000Hz_IQ.wav"
# -i = "../samples/image_noaa_2.png"
# -o = "image_desc.json"
# -t = "../tle/noaa_May_2019.txt"

if __name__ == "__main__":
    main()
