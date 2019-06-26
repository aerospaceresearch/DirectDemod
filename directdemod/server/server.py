import os
import re
import json
import time
import atexit

from shutil import copyfile
from flask import Flask, render_template, send_file, abort, request, g
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

conf_path = app.root_path + "/conf.json"
conf = json.load(open(conf_path, 'r'))
RATE = int(conf["update_rate"])

start_date = time.time()
pattern = re.compile("SDRSharp_[0-9]{8}_[0-9]{6}Z_[0-9]{9}Hz_IQ.png$")


def get_interval(start_time, rate):
    return time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(start_time)) + "_" + \
           time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(start_time + rate))


@app.route('/upload.html', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        dir_path = app.root_path + "/images/img" + get_interval(start_date, RATE)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        for key in request.files.keys():
            f = request.files[key]
            if bool(pattern.match(f.filename)):
                f.save(dir_path + "/" + request.form["sat_type"] + "_" + f.filename)

    return render_template('upload.html', conf=json.dumps(conf))


@app.route('/map.html')
@app.route('/map')
def map_page():
    return render_template('map.html', conf=json.dumps(conf))


@app.route('/globe.html')
@app.route('/globe')
def globe_page():
    return render_template('globe.html', conf=json.dumps(conf))


@app.route('/tms/<path:file>', methods=['GET'])
def get_tms(file):
    file_name = app.root_path + "/tms/" + file
    if not os.path.isfile(file_name):
        abort(404)
    return send_file(file_name)


def update():
    global start_date
    interval = get_interval(start_date, RATE)
    dir_path = app.root_path + "/images/img" + interval

    if not os.path.isdir(dir_path) or len(os.listdir(dir_path)) == 0:
        start_date += RATE
        return

    images = os.listdir(dir_path)
    tms_path = app.root_path + "/tms/tms" + interval
    process(dir_path, tms_path, images)
    start_date += RATE
    move_unprocessed_files(dir_path, images)

    conf[conf["counter"]] = interval
    conf["counter"] += 1


def move_unprocessed_files(dir_path, images):
    dimages = set(images)
    dgeo = set(map(lambda x: os.path.splitext(x)[0] + "_geo.tif", dimages))
    not_processed = []

    for f in os.listdir(dir_path):
        if f not in dimages and f not in dgeo and f != "merged.tif":
            not_processed.append(f)

    if len(not_processed) > 0:
        new_dir_path = app.root_path + "/images/img" + get_interval(start_date, RATE)
        os.mkdir(new_dir_path)

        for f in not_processed:
            os.rename(dir_path + "/" + f, new_dir_path + "/" + f)


def process(dir_path, tms_path, images):
    from directdemod.misc import save_metadata, preprocess
    from directdemod.georeferencer import Georeferencer, set_nodata
    from directdemod.merger import merge
    from directdemod.constants import TLE_NOAA

    sat_types = list(map(lambda f: f[0:7], images))
    images = list(map(lambda f: dir_path + "/" + f, images))
    georeferenced = list(map(lambda f: os.path.splitext(f)[0] + "_geo.tif", images))
    referencer = Georeferencer(tle_file=TLE_NOAA)

    for index, val in enumerate(images):
        try:
            preprocess(val, georeferenced[index])
            save_metadata(file_name=val,
                          image_name=georeferenced[index],
                          sat_type=sat_types[index],  # extracting NOAA satellite
                          tle_file=TLE_NOAA)
            referencer.georef_tif(georeferenced[index], georeferenced[index])
        except Exception as e:
            print(e)
            # FIXME: add logging
            continue

    merged_file = dir_path + "/merged.tif"
    if len(georeferenced) > 1:
        merge(georeferenced, output_file=merged_file)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " + merged_file + " " + tms_path)
    elif len(georeferenced) == 1:
        copyfile(georeferenced[0], merged_file)
        set_nodata(merged_file, value=0)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " + merged_file + " " + tms_path)


def save_conf():
    with open("conf.json", 'w') as out:
        json.dump(conf, out)


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update, trigger="interval", seconds=RATE)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    atexit.register(lambda: save_conf())


main()  # DON'T  ADD __name__ == '__main__'
