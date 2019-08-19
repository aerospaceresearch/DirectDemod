"""
This module contains functions needed for easy upload of files
to the web server.
"""
import os

from PIL import Image
from typing import List
from scipy.ndimage import rotate
from directdemod import constants
from directdemod.misc import save_metadata
from directdemod.georeferencer import Georeferencer


def preprocess_a(image_name: str, output_file: str) -> None:
    """preprocesses first part of image"""
    preprocess(image_name, output_file, 85, 995)


def preprocess_b(image_name: str, output_file: str) -> None:
    """preprocesses second part of image"""
    preprocess(image_name, output_file, 1125, 2035)


def preprocess(image_name: str, output_file: str, lo: int, hi: int) -> None:
    """function opens the image, crops it according to given bounds, rotates it on 180
    degrees and saves to output_file

    Args:
        image_name (:obj:`string`): path to the input image
        output_file (:obj:`string`): path to output file, where result image will be saved
        lo (:obj:`int`): left cropping bound of the image
        hi (:obj:`int`): right cropping bound of the image
    """

    image = Image.open(image_name)
    _, height = image.size
    image = image.crop((lo, 0, hi, height))
    image = rotate(image, 180)
    Image.fromarray(image).save(output_file)


def process(path: str, sat_type: str) -> List[str]:
    """decodes recording in path (should be in .wav format), applies preprocessing, georeferencing both parts
    and sends both parts of the image to the server via ssh (scp command)

    Args:
        path (:obj:`str`): path to NOAA recording
        sat_type (:obj:`str`): type of the NOAA satellite (i. e. "NOAA 19")
    """

    file_name = os.path.basename(path)
    dir_path = os.path.dirname(path)

    os.system("python3 " + constants.MODULE_PATH + "/main.py --tle=" + constants.TLE_NOAA + " -f " +
              str(constants.SAT_FREQ[sat_type]) + " -d noaa " + path)

    image_name = os.path.splitext(file_name)[0] + "_f1.png"
    tiff_name = os.path.splitext(file_name)[0] + ".tif"
    image_a, image_b = dir_path + "/" + "A_" + tiff_name, dir_path + "/" + "B_" + tiff_name

    preprocess_a(dir_path + "/" + image_name, image_a)
    preprocess_b(dir_path + "/" + image_name, image_b)

    referencer = Georeferencer(tle_file=constants.TLE_NOAA)

    save_metadata(file_name=file_name,
                  image_name=image_a,
                  sat_type=sat_type,
                  tle_file=constants.TLE_NOAA)

    save_metadata(file_name=file_name,
                  image_name=image_b,
                  sat_type=sat_type,
                  tle_file=constants.TLE_NOAA)

    referencer.georef_tif(image_a, image_a)
    referencer.georef_tif(image_b, image_b)

    return [image_a, image_b]


def send(files: List[str]) -> None:
    """sends all images to web server"""
    for image in files:
        os.system("sshpass -p '" + constants.PASS + "' scp " + image + " " + constants.USER +
                  "@" + constants.IP + ":" + constants.DIR)


def remove(files: List[str]) -> None:
    """removes all passed files"""
    for image in files:
        if os.path.isfile(image):
            os.remove(image)


def process_files(files: List[str], sat_types: List[str]) -> None:
    """processes list of files, calls process() one each pair"""
    processed = []
    for index, val in enumerate(files):
        processed.extend(process(val, sat_types[index]))

    send(processed)
    remove(processed)
