"""
Tools for data extraction and json manipulations.
These classes provide API for the input/output operations
with json files.
"""
import os.path
import json
import argparse

from typing import Any
from datetime import datetime, timedelta

import numpy as np
import tifffile

from PIL import Image
from scipy.ndimage import rotate
from pyorbital.orbital import Orbital
from directdemod import constants


class Encoder(json.JSONEncoder):
    """
    JSON encoder, which handles `np.ndarray` and `datetime` objects
    """

    def default(self, obj) -> Any:
        """Encode the object

        Args:
            obj (:obj:`object`): oject to encode

        Returns:
            :obj:`object`: encoded object
        """

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(Encoder, self).default(obj)


def to_datetime(image_time: str, image_date: str) -> datetime:
    """builds datetime object

    Args:
        image_time (:obj:`string`): time when the image was captured
        image_date (:obj:`string`): date when the image was captured

    Returns:
        :obj:`datetime`: contructed datetime object

    Throws:
        :obj:`ValueError`: if length of date string is not 8 or length  of time string is not 6
    """

    if len(image_date) != 8 or len(image_time) != 6:
        raise ValueError('ERROR: Invalid length of input dates.')

    try:
        year = int(image_date[0:4])
        month = int(image_date[4:6])
        day = int(image_date[6:8])
        hour = int(image_time[0:2])
        minute = int(image_time[2:4])
        second = int(image_time[4:6])

        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        # add error logging
        raise


def compute_alt(orbiter: Orbital, dtime: datetime, image: np.ndarray,
                step: float) -> tuple:
    """compute coordinates of the satellite, shifts the position for step pixels

    Args:
        orbiter (:obj:`Orbital`): object representing orbit of satellite
        dtime (:obj:`datetime`): time when the image was captured
        image (:obj:`np.array`): captured image
        step (:obj:`float`): distance shift, couting from start of recording

    Returns:
        :obj:`tuple`: coordinates of satellite at certain point of time
    """

    return orbiter.get_lonlatalt(dtime + timedelta(
        seconds=int(image.shape[0] / 4) + step))[:2][::-1]


def extract_date(filename: str) -> datetime:
    """extracts date from filename

    Args:
        filename (:obj:`string`): name of the file

    Returns:
        :obj:`datetime`: extracted datetime object

    Throws:
        :obj:`ValueError`: if provided filename doesn't correspond to default SDR format
    """

    parts = filename.split('_')
    image_date, image_time = None, None
    for index, part in reversed(list(enumerate(parts))):
        if part[-1] == "Z":
            image_time = part[:-1]
            image_date = parts[index - 1]

    if image_date is None or image_time is None:
        raise ValueError("ERROR: Invalid file name format \'" + str(filename) +
                         "\'.")

    return to_datetime(image_time, image_date)


def extract_coords(image: np.ndarray,
                   satellite: str,
                   dtime: datetime,
                   tle_file: str = None) -> tuple:
    """extracts coordinates of the image bounds

    Args:
        image (:obj:`np.array`): captured image
        satellite (:obj:`string`): name of the satellite
        dtime (:obj:`datetime`): time when the satellite was in the center of the image
        tle_file (:obj:`string`): path to tle file

    Returns:
        :obj:`tuple`: extracted coordinates
    """

    orbiter = Orbital(satellite) if tle_file is None else Orbital(
        satellite, tle_file=tle_file)
    delta = int(image.shape[0] / 16)
    delta = max(delta, 10)

    top_coord = compute_alt(orbiter, dtime, image, -delta)
    bot_coord = compute_alt(orbiter, dtime, image, delta)
    center_coord = compute_alt(orbiter, dtime, image, 0)

    return top_coord, bot_coord, center_coord


def compute_angle(lat1: float, long1: float, lat2: float,
                  long2: float) -> float:
    """compute angle between 2 points, defined by latitude and longitude

    Args:
        lat1 (:obj:`float`): latitude of start point
        long1 (:obj:`float`): longitude of start point
        lat2 (:obj:`float`): latitude of end point
        long2 (:obj:`float`): longitude of end point

    Returns:
        :obj:`float`: angle between points
    """

    # source: https://stackoverflow.com/questions/3932502/
    # calculate-angle-between-two-latitude-longitude-points
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


def create_desc(file_name: str,
                image_name: str,
                sat_type: str = "NOAA 19",
                tle_file: str = None) -> dict:
    """create descriptor file for audio record

    Args:
        file_name (:obj:`string`): path to audio record
        image_name (:obj:`string`): path to image file
        sat_type (:obj:`string`): name of the satellite
        tle_file (:obj:`string`): path to tle file

    Returns:
        :obj:`dict`: returns extracted descriptor file
    """

    image = np.array(Image.open(image_name))

    dtime = extract_date(file_name)
    top, bot, center = extract_coords(image,
                                      sat_type,
                                      dtime,
                                      tle_file=tle_file)
    degree = compute_angle(*bot, *top)

    descriptor = {
        "image_name": os.path.abspath(image_name),
        "sat_type": sat_type,
        "date_time": dtime,
        "center": list(center),
        "direction": degree
    }

    return descriptor


def save_metadata(file_name: str,
                  image_name: str,
                  sat_type: str = "NOAA 19",
                  tle_file: str = None) -> None:
    """creates descriptor from file_name and embeds it into the image in
    tif format. If the image provided is not tif, then creates new image

    Args:
        file_name (:obj:`string`): path to audio record
        image_name (:obj:`string`): path to image file (.tif)
        sat_type (:obj:`string`): name of the satellite
        tle_file (:obj:`string`): path to tle file
    """

    name, _ = os.path.splitext(image_name)
    image = np.array(Image.open(image_name))

    descriptor = create_desc(file_name,
                             image_name,
                             sat_type=sat_type,
                             tle_file=tle_file)

    tifffile.imsave(name + '.tif',
                    image,
                    description=json.dumps(descriptor, cls=Encoder))


def preprocess(image_name: str, output_file: str) -> None:
    """preprocesses the image, crops it and rotates for 180 degrees
    result is saved in output_file file

    Args:
        image_name (:obj:`string`): path to image file
        output_file (:obj:`string`): path to output file
    """

    image = Image.open(image_name)
    _, height = image.size
    image = image.crop((85, 0, 995, height))
    image = rotate(image, 180)
    Image.fromarray(image).save(output_file)


def main() -> None:
    """Descriptor CLI interface"""
    parser = argparse.ArgumentParser(
        description="Embed data from SDR into tif image")
    parser.add_argument('-f',
                        '--file_sdr',
                        required=True,
                        help='Path to recorded SDR file.')
    parser.add_argument('-i',
                        '--image_name',
                        required=True,
                        help='Path to decoded image.')
    parser.add_argument('-t',
                        '--tle',
                        required=False,
                        help='Path to tle file.')
    parser.add_argument('-s',
                        '--sat_type',
                        required=False,
                        help='Satellite type. \'NOAA 19\' by default.',
                        default="NOAA 19")

    args = parser.parse_args()

    filename = args.file_sdr
    image_name = args.image_name
    sat_type = args.sat_type

    allowed_sats = {'NOAA 18', 'NOAA 19', 'NOAA 15'}

    if sat_type not in allowed_sats:
        raise ValueError('ERROR: Invalid satellite type: {0}'.format(sat_type))

    tle_file = args.tle

    if tle_file is None:
        tle_file = constants.TLE_NOAA

    if not os.path.isfile(tle_file):
        raise ValueError("ERROR: Tle file doesn't exist {0}".format(tle_file))

    save_metadata(filename, image_name, sat_type, tle_file)


# Example arguments
# -f = "../samples/SDRSharp_20190521_152538Z_137500000Hz_IQ.wav"
# -i = "../samples/image_noaa_2.png"

if __name__ == "__main__":
    main()
