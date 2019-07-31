###### Variable settings

import os
import directdemod as demod

MODULE_PATH = os.path.abspath(os.path.join(list(demod.__path__)[0], os.pardir))

## IQ.wav settings
IQ_FREQOFFSET = 30000
IQ_SDRSAMPRATE = 2.048e6

## Processing settings
PROC_CHUNKSIZE = 20000000

## NOAA settings
NOAA_FMBW = 60000
NOAA_AUDSAMPRATE = 20800
NOAA_FREQ = 137620000
NOAA_CRUDESYNCSAMPRATE = 40960
NOAA_T = 1.0/4160 #Time of one bit
NOAA_SYNCA = [0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
NOAA_SYNCB = [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0]
NOAA_PEAKHEIGHTWIGGLE = 0.25 # %allowable change in peak height
NOAA_MINPEAKDIST = 0.45 # min distance between two sync in seconds
NOAA_COLORCORRECT_FIFOLEN = 10000
NOAA_DETECTMAXCHANGE = 5
NOAA_DETECTCONSSYNCSNUM = 10
NOAA_SATS = {137620000:"NOAA 15", 137100000:"NOAA 19", 137912500:"NOAA 18"}
SAT_FREQ = {"NOAA 15": 137620000, "NOAA 19": 137100000, "NOAA 18": 137912500}

## Merger settings
RESOLUTION = 500
COLOR = "black"

## Georeferencer settings
TEMP_TIFF_FILE = "_temp.tif"
TEMP_VRT_FILE = "_vrt.vrt"
DEFAULT_RS = "EPSG:4326"

TLE_NOAA = MODULE_PATH + "/tle/noaa18_June_14_2018.txt"
BORDERS = MODULE_PATH + "/misc/shapes/borders.shp"  # should be used in directdemod directory

## MAP
MAP_TEMPLATE = MODULE_PATH + "/misc/map.html"
GLOBE_TEMPLATE = MODULE_PATH + "/misc/globe.html"

## SSH settings
USER = ""
IP = ""
PASS = ""
DIR = "/home/main/DirectDemod/directdemod/server/ftp"

###### Do not change these

## Source types
SOURCE_IQWAV = 0
SOURCE_IQDAT = 1

## Filter types
FLT_LP = 0
FLT_HP = 1
FLT_BP = 2
FLT_BS = 3

## Chunker var names
CHUNK_FREQOFFSET = "freqoffset"
CHUNK_BWLIM = "bwlim"
