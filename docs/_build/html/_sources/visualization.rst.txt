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

.. autoclass:: directdemod.merger.ImageMerger
   :members:

   .. automethod:: __init__

Georeferencer
---------------

This class provides an API for image georeferencing.
Sample command to run georeferencer.py:
``python georeferencer.py -f ../samples/image_noaa19_1_desc.json -o ../samples/image_noaa19_2.tif.``
Console options:

-f     path to descriptor file
-o     path to output file

.. autoclass:: directdemod.georeferencer.Georeferencer
   :members:

   .. automethod:: __init__

Library checker
---------------

.. autoclass:: directdemod.misc.Checker
   :members:

   .. automethod:: __init__

Json encoder
------------

.. autoclass:: directdemod.misc.Encoder
   :members:

   .. automethod:: __init__

Json parser
------------

.. autoclass:: directdemod.misc.JsonParser
   :members:

   .. automethod:: __init__
