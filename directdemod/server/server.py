import os
import re
import json
import atexit

from shutil import copyfile
from flask import Flask, render_template, send_file, abort, request, g
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
conf_path = app.root_path + "/conf.json"
counter = int(json.load(open(conf_path, 'r'))["counter"])
pattern = re.compile("SDRSharp_[0-9]{8}_[0-9]{6}Z_[0-9]{9}Hz_IQ.png$")


@app.route('/index.html')
@app.route('/')
def index():
    return "Starting page."


@app.route('/upload.html', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        dir_path = app.root_path + "/images/img" + str(counter)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        for key in request.files.keys():
            f = request.files[key]
            if bool(pattern.match(f.filename)):
                print("Saved: " + dir_path + "/" + f.filename)
                f.save(dir_path + "/" + f.filename)

    return render_template('upload.html', counter=counter)


@app.route('/map.html')
@app.route('/map')
def map_page():
    return render_template('map.html', counter=counter)


@app.route('/globe.html')
@app.route('/globe')
def globe_page():
    return render_template('globe.html', counter=counter)


@app.route('/tms/<path:file>', methods=['GET'])
def get_tms(file):
    file_name = app.root_path + "/tms/" + file
    if not os.path.isfile(file_name):
        abort(404)
    return send_file(file_name)


def update():
    global counter
    dir_path = app.root_path + "/images/img" + str(counter)
    if not os.path.isdir(dir_path) or len(os.listdir(dir_path)) == 0:
        return None

    print("Starting update.")
    counter += 1
    images = os.listdir(dir_path)
    print("Found files:")
    print(images)
    process(dir_path, app.root_path + "/tms/tms" + str(counter - 1), images)


def process(dir_path, tms_path, images):
    from directdemod.misc import save_metadata, preprocess
    from directdemod.georeferencer import Georeferencer, set_nodata
    from directdemod.merger import merge
    from directdemod.constants import TLE_NOAA

    print("Preparing to georeference.")
    images = list(map(lambda f: dir_path + "/" + f, images))
    georeferenced = list(map(lambda f: os.path.splitext(f)[0] + "_geo.tif", images))
    referencer = Georeferencer(tle_file=TLE_NOAA)
    print(georeferenced)
    for index, val in enumerate(images):
        print("Georeferencing at index: " + str(index))
        try:
            preprocess(val, georeferenced[index])
            save_metadata(file_name=val,
                          image_name=georeferenced[index],
                          sat_type="NOAA 19",
                          tle_file=TLE_NOAA)
            referencer.georef_tif(georeferenced[index], georeferenced[index])
        except Exception as e:
            print(e)
            continue

    print("Preparing for outputing mergef file.")
    merged_file = dir_path + "/merged.tif"
    if len(georeferenced) > 1:
        print("Multi tms.")
        merge(georeferenced, output_file=merged_file)
        set_nodata(merged_file, value=255)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " + merged_file + " " + tms_path)
    elif len(georeferenced) == 1:
        print("Tms for single file.")
        copyfile(georeferenced[0], merged_file)
        set_nodata(merged_file, value=255)
        os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " + merged_file + " " + tms_path)
    else:
        global counter
        counter -= 1


def save_counter():
    if counter is not None:
        d = {"counter": counter}
        with open("conf.json", 'w') as out:
            json.dump(d, out)


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update, trigger="interval", seconds=20)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    atexit.register(lambda: save_counter())


main()  # DON'T  ADD __name__ == '__main__'
