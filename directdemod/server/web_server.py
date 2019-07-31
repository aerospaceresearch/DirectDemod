"""
This module provides an functionality for implementing flask
web-server, which supports displaying NOAA images.
"""
import os
import re
import json
import time
import atexit

from typing import List
from shutil import copyfile, move
from osgeo import gdal
from flask import Flask, render_template, send_file, abort, request
from apscheduler.schedulers.background import BackgroundScheduler

APP = Flask(__name__)

FTP_DIR = APP.root_path + "/ftp"
CONF_PATH = APP.root_path + "/conf.json"
conf = json.load(open(CONF_PATH, 'r'))
RATE = int(conf["update_rate"])

start_date = time.time()
PATTERN = re.compile("[AB]_SDRSharp_[0-9]{8}_[0-9]{6}Z_[0-9]{9}Hz(_IQ)?\\.(tif|tiff)$")


def get_interval(start_time: float, rate: int) -> str:
    """computes the interval and returns it's string representation

    Args:
        start_time (:obj:`float`): start of the interval
        rate (:obj:`int`): width of the interval in seconds

    Returns:
        :obj:`string`:
    """

    return time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(start_time)) + "_" + \
           time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(start_time + rate))


@APP.route('/upload.html', methods=['GET', 'POST'])
@APP.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """renders upload.html page"""
    if request.method == 'POST':
        dir_path = APP.root_path + "/images/img" + get_interval(
            start_date, RATE)

        files = []
        for key in request.files.keys():
            file = request.files[key]
            if bool(PATTERN.match(file.filename)):
                files.append(file)

        if not os.path.isdir(dir_path) and len(files) > 0:
            os.mkdir(dir_path)

        for f in files:
            path = dir_path + "/" + f.filename
            f.save(path)
            if not valid(path):
                os.remove(path)

        if os.path.isdir(dir_path) and len(os.listdir(dir_path)) == 0:
            os.rmdir(dir_path)

    return render_template('upload.html', conf=json.dumps(conf))


@APP.route('/map.html')
@APP.route('/map')
def map_page():
    """renders map.html page"""
    return render_template('map.html', conf=json.dumps(conf))


@APP.route('/globe.html')
@APP.route('/globe')
def globe_page():
    """renders globe.html page"""
    return render_template('globe.html', conf=json.dumps(conf))


@APP.route('/tmsA/<path:file>', methods=['GET'])
def get_tms_a(file: str):
    """gets file from tms directory

    Args:
        file (:obj:`string`): name of file from tms directory
    """

    file_name = APP.root_path + "/tmsA/" + file
    if not os.path.isfile(file_name):
        abort(404)
    return send_file(file_name)


@APP.route('/tmsB/<path:file>', methods=['GET'])
def get_tms_b(file: str):
    """gets file from tms directory

    Args:
        file (:obj:`string`): name of file from tms directory
    """

    file_name = APP.root_path + "/tmsB/" + file
    if not os.path.isfile(file_name):
        abort(404)
    return send_file(file_name)


def valid(path: str) -> bool:
    data = gdal.Open(path)
    return data is not None


def move_files(ftp_dir: str, dir_path: str) -> None:
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    for f in os.listdir(ftp_dir):
        move(f, dir_path)


def update() -> None:
    """processes data collected during this interval and
    saves the update, so it will be displayed during next
    page renders
    """

    global start_date
    interval = get_interval(start_date, RATE)
    dir_path = APP.root_path + "/images/img" + interval
    move_files(FTP_DIR, dir_path)

    if not os.path.isdir(dir_path) or not os.listdir(dir_path):
        start_date += RATE
        return

    images_a = [im for im in os.listdir(dir_path) if im.startswith("A_")]
    images_b = [im for im in os.listdir(dir_path) if im.startswith("B_")]

    tms_path_a = APP.root_path + "/tmsA/tms" + interval
    tms_path_b = APP.root_path + "/tmsB/tms" + interval

    process(dir_path, tms_path_a, "a", images_a)
    process(dir_path, tms_path_b, "b", images_b)

    start_date += RATE
    # move_unprocessed_files(dir_path, images)

    conf[conf["counter"]] = interval
    conf["counter"] += 1


#  FIXME: delete?
def move_unprocessed_files(dir_path: str, images: List[str]) -> None:
    """moves all unprocessed files to the next time interval

    Args:
        dir_path (:obj:`str`): path to images directory
        images (:obj:list[str]): list of images paths
    """

    dimages = set(images)
    dgeo = set(map(lambda x: os.path.splitext(x)[0] + "_geo.tif", dimages))
    not_processed = []

    for file in os.listdir(dir_path):
        if file not in dimages and file not in dgeo and file != "merged.tif":
            not_processed.append(file)

    if not_processed:
        new_dir_path = APP.root_path + "/images/img" + get_interval(
            start_date, RATE)
        os.mkdir(new_dir_path)

        for file in not_processed:
            os.rename(dir_path + "/" + file, new_dir_path + "/" + file)


def process(dir_path: str, tms_path: str, image_part: str, images: List[str]) -> None:
    """processes all images from `images` array, merges them and creates tms
    which is store in `tms_path`

    Args:
        dir_path (:obj:`str`): path to images directory
        tms_path (:obj:`str`): path to tms directory
        image_part (:obj:`str`): name of image part ("A" or "B")
        images (:obj:list[str]): list of images paths
    """

    from directdemod.georeferencer import set_nodata
    from directdemod.merger import merge

    images = list(map(lambda f: dir_path + "/" + f, images))
    merged_file = dir_path + "/" + image_part + "_merged.tif"
    if len(images) > 1:
        merge(images, output_file=merged_file)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " +
                  merged_file + " " + tms_path)
    elif len(images) == 1:
        copyfile(images[0], merged_file)
        set_nodata(merged_file, value=0)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " +
                  merged_file + " " + tms_path)

    save_conf()


def save_conf() -> None:
    """saves configuration file"""
    with open(CONF_PATH, 'w') as out:
        json.dump(conf, out)


def main() -> None:
    """registers scheduler jobs and onExit functions"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update, trigger="interval", seconds=RATE)
    scheduler.start()
    atexit.register(scheduler.shutdown)
    atexit.register(save_conf)


main()  # DON'T  ADD __name__ == '__main__'

if __name__ == "__main__":
    APP.run()
