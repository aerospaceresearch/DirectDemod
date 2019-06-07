.. DirectDemod documentation master file, created by
   sphinx-quickstart on Thu May 17 00:16:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Visualizations routine
======================

In this section are presented classes that are related to visualization of satellite imagery,
along with their helper classes, which provide IO operations.

Image merger
------------

Merger provides functionality, along with CLI interface, for merging several raster images.
Merger supports several methods for overlapping parts of the images: `average`, `max`, `first`, `last`.

``python merger.py -o o.tif -r average --files a.tif b.tif``

Console options:

-f, --files      list of files to merge
-o, --output     name of output file
-r, --resample   name of resample algorithm

.. automodule:: directdemod.merger
   :members:

Georeferencer
---------------

This class provides an API for image georeferencing.
Sample command to run georeferencer.py:

``python georeferencer.py -m -i ../samples/decoded/SDRSharp_20190521_170204Z_137500000Hz.tif``

Console options:

-m, --map       flag to create map overlay
-i, --image     path to image file

.. autoclass:: directdemod.georeferencer.Georeferencer
   :members:

   .. automethod:: __init__


Map generation
--------------

To generate visualization of raster use `generate_map.py` interface.
The following command will generate a TMS (Tile Map Service) and 2 visualization files in
`samples/tms` directory.

``python generate_map.py --raster ../samples/decoded/raster.tif --tms ../samples/tms``

You can run `map.html` by opening in the browser.

To use `globe.html` go to tms directory and type the following command to start http server on port 8000 (for python3):

``python -m http.server 8000``

Then open browser and go to `http://localhost:8000/globe.html`.

Library checker
---------------

.. autoclass:: directdemod.misc.Checker
   :members:

   .. automethod:: __init__

Json encoder
------------
Json encoder, which handles encoding numpy array and datetime objects.

.. autoclass:: directdemod.misc.Encoder
   :members:

   .. automethod:: __init__

Json parser
------------
JS-style wrapper around json, which uses provided Json encoder.

.. autoclass:: directdemod.misc.JSON
   :members:

   .. automethod:: __init__
