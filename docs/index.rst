.. DirectDemod documentation master file, created by
   sphinx-quickstart on Thu May 17 00:16:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DirectDemod's documentation!
=======================================

DirectDemod is a set of python libraries that allow for easy handling, demodulation and decoding of raw IQ.wav (or IQ.dat) files directly captured from RTLSDRs. All the tools such as file readers, filters, chunking etc. are implemented and can be used as per the user's needs. Currently application specific demodulators are implemented for NOAA satellites (Image and sync detection), Funcube (similar cubesats) and Meteor M2 satellite (sync detection).

To get started on directly using this software for decoding: NOAA or demodulating: funcubes or meteor m2 satellites, look at the getting started guide.
Some tutorials on how to use the modules and write your own scripts or to extend existing libraries, can be found at the tutorial folder in the repo.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   gettingstarted.rst
   modules.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
