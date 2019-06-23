from flask import Flask, render_template, send_file, abort
import os

app = Flask(__name__)


@app.route('/index.html')
@app.route('/')
def index():
    return "Start page."


@app.route('/map.html')
@app.route('/map')
def map_page():
    return render_template('map.html')


@app.route('/globe.html')
@app.route('/globe')
def globe_page():
    return render_template('globe.html')


@app.route('/tms/<path:file>', methods=['GET'])
def get_tms(file):
    file_name = app.root_path + "/tms/" + file
    if not os.path.isfile(file_name):
        abort(404)
    return send_file(file_name)
