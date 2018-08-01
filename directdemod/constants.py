###### Variable settings

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