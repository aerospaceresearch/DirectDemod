.. DirectDemod documentation master file, created by
   sphinx-quickstart on Thu May 17 00:16:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutorials
======================

This section presents several usage examples of directdemod package.
Each usage example is accompanied with thorough explanation and
an appropriate data, which is stored in `tutorial/data/` folder.

*Note:* python version should be higher then 3.6, preferably 3.7.
In tutorials below `python` command refers to python3.

*Note on warnings*: depending on your python version you can see the following warnings,
which is ok, they are not the errors of the program.

 - YAMLLoadWarning: calling yaml.load() without Loader=... is deprecated
 - Warning 1: TIFFReadDirectoryCheckOrder:Invalid TIFF directory; tags are
   not sorted in ascending order

Data extraction (misc.py)
--------------------------

`misc.py` script is used to perform data extraction of satellite parameters. When running, `misc.py`
will extract data from SDR file, create copy of provided image with .tif extension and embed
extracted data as json into it. CLI interface receives following console options:

-f, --file_sdr  path to recorded SDR file
-i, --image_name  path to decoded and preprocessed image
-t, --tle  path to tle file
-s, --sat_type  satellite type

Tle and satellite type parameters are optional.
The `tutorial/data/metadata` directory contains sample files - sdr file and the decoded image.
Sample command:
::

    python directdemod/misc.py -f tutorial/data/metadata/SDRSharp_20190521_170204Z_137500000Hz_IQ.wav \
    -i tutorial/data/metadata/image.png

Created `image.tif` file will contain the satellite data (orbit parameters, satellite type etc. )
in json format along with the image itself; it will be ready for performing georeferencing.

Georeferencer
----------------------

Georeferencer class is intended to provide methods for georeferencing NOAA images.
It provides CLI interface for running the program from command line. CLI interface takes following
options (map, resample and output_file are optional):

-i, --image_name  path to image file
-o, --output_file  name of output file
-m, --map  flag to create map overlay
-r, --resample  resample algorithm

Georeferencer assumes that the image passed via `--image_name` option contains a descriptor file
embedded within it. If the file doesn't contain it, the processing will result in an error.

As an example usage let's say we have a decoded and preprocessed NOAA image `start.png` and the file
it was extracted from `SDRSharp_20190521_170204Z_137500000Hz_IQ.wav`. To receive a georeferenced image
we need to do the following:

1. Extract the information from `.wav` file name and save it to `start.tif` file.
2. Georeference tif file.

To extract data `misc.py` command is used (see misc.py docs).
::

    python directdemod/misc.py -f tutorial/data/georef/SDRSharp_20190521_170204Z_137500000Hz_IQ.wav \
    -i tutorial/data/georef/start.png


To georeference the file we use `georeferencer.py` file. `start.tif` will contain georeferenced image.
::

    python directdemod/georeferencer.py -i tutorial/data/georef/start.tif

Map Overlay
----------------

Map overlay can be created using `--map` option of the georeferencer. After the georeferencing is done
map borders shapefile will be overlayed on top of it.

To create an overlay over image use the following command.
::

    python directdemod/georeferencer.py -m -i tutorial/data/overlay/no_overlay.tif \
    -o tutorial/data/overlay/with_overlay.tif

Merger
---------------

Merge is used to combine several georeferenced images into one single raster, taking care
of overlapping regions. Merger CLI interface has following console options:

-f, --files  list of input files
-o, --output  name of output file
-r, --resample  resample algorithm

Resample option receives one of the four merging method names:

1. first
2. last
3. average
4. max

The `tutorial/data/merge` directory contains several example usage files. `image1.tif` and
`image2.tif` are sample files for merging. Use following command to merge them (resample average):
::

   python directdemod/merger.py -o tutorial/data/merge/merged.tif -r average \
   --files tutorial/data/merge/image1.tif tutorial/data/merge/image2.tif

The `tutorial/data/merge/merged.tif` file will be created after running the above command.
You can compare it with other merging methods (`average.tif`, `max.tif`, `first.tif`, `last.tif`).

Map generation tutorial
-----------------------

To generate visualization of raster use `generate_map.py` interface.
The following command will generate a TMS (Tile Map Service) and 2 visualization files in
`samples/tms` directory.

::

   python directdemod/generate_map.py --raster samples/decoded/raster.tif --tms samples/tms

You can run `map.html` by opening it directly in the browser.
To run `globe.html` go to tms directory and start the http server on port 8000 (python3):
::

   python -m http.server 8000

Then open browser and go to `http://localhost:8000/globe.html`.

Help
-----------------------

If you encountered an error or want to add a fix, you can contact us directly on
``github.com/aerospaceresearch/DirectDemod``.