.. DirectDemod documentation master file, created by
   sphinx-quickstart on Thu May 17 00:16:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DirectDemod: Getting Started
===================================

Installation
-----------------------
DirectDemod is written in python3 and uses the following libraries:

Mandatory:

* scipy

* numpy

* matplotlib

* PIL

* colorsys

Optional: (Only used for map overlay for NOAA images)

* pyorbital

* Basemap

* cartopy

Please make sure you have all the mandatory libraries installed.

Clone the repo into a folder and run "python main.py". If you get a usage statement, you are good to go. The usage statement has all the commands that can be given to the program.

Specific applications
-----------------------

Following are the application specific guides. Assuming you already know how to record RTLSDR data to a .wav or a .dat file.

To decode NOAA image
-----------------------

If you want to decode a NOAA IQ data into images you can run the command:

    python main.py -c 137000000 -f 137100000 -d noaa "file.wav"

here 13700000 is the centre frequency of the input file. 137100000 is the frequency of the satellite. "-d noaa" tells the program to use a noaa decoder on this. You should change these to match the file you have. When you run this, it will continuously print the status of decoding.

If you are skeptical if these settings are right and just want to test a portion of your file you can use the -s and -e options. For example if I want to just decode the file from 1000000 sample number to 2000000 sample number I can use the command,

	python main.py -c 137000000 -f 137100000 -s 1000000 -e 2000000 -d noaa "file.wav"

This is especially helpful to just do a small test run to make sure it has found the signal.

This will just generate a black and white image, and a color image if right channels are detected. You can have a look at other commands from the usage statement.

In case the signal is not found or is very noisy you can do the following trouble shooting:

* sometimes I and Q channels migt be swapped, so use the -q flag to try to un-swap and try decoding.
	e.g. python main.py -c 137000000 -f 137100000 -q -d noaa "file.wav"

* If the signal is very noisy, you can play around with the bandwidth of the main filter by using the -b option
	e.g. python main.py -c 137000000 -f 137100000 -b 1000000 -d noaa "file.wav"

* Try opening the file in a gui like SDRSHARP and make sure you can see and hear the characteristic NOAA waterfall. Note down the frequency and make sure you are providing accurate inputs to the program.

To get sync locations in IQ recordings
--------------------------------------------
Currently the program has implementations of NOAA, Meteor M2 and Funcube (similar cubesats) so that accurate sync locations within the file could be found.

Similar to NOAA image extraction, if you provide the flag -sync, the program will generate a .csv file with the corresponding sync locations.
For Funcube or Meteor satellites, the process is similar, but no need to pass -sync flag, the .csv file will be automatically generated.