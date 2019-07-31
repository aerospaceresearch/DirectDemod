import os

from PIL import Image
from typing import List
from scipy.ndimage import rotate
from directdemod import constants
from directdemod.misc import save_metadata
from directdemod.georeferencer import Georeferencer


def preprocess_a(image_name: str, output_file: str) -> None:
    preprocess(image_name, output_file, 85, 995)


def preprocess_b(image_name: str, output_file: str) -> None:
    preprocess(image_name, output_file, 1125, 2035)


def preprocess(image_name: str, output_file: str, lo: int, hi: int) -> None:
    image = Image.open(image_name)
    _, height = image.size
    image = image.crop((lo, 0, hi, height))
    image = rotate(image, 180)
    Image.fromarray(image).save(output_file)


def process(path: str, sat_type: str) -> None:
    file_name = os.path.basename(path)
    dir_path = os.path.dirname(path)

    os.system("python3 " + constants.MODULE_PATH + "/main.py --tle=" + constants.TLE_NOAA + " -f " +
              str(constants.SAT_FREQ[sat_type]) + " -d noaa " + path)

    image_name = os.path.splitext(file_name)[0] + ".png"
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

    os.system("sshpass -p '" + constants.PASS + "' scp " + image_a + " " + constants.USER +
              "@" + constants.IP + ":" + constants.DIR)

    os.system("sshpass -p '" + constants.PASS + "' scp " + image_b + " " + constants.USER +
              "@" + constants.IP + ":" + constants.DIR)

    if os.path.isfile(image_a):
        os.remove(image_a)
    if os.path.isfile(image_b):
        os.remove(image_b)


def process_files(files: List[str], sat_types: List[str]) -> None:
    for index, val in enumerate(files):
        process(val, sat_types[index])
