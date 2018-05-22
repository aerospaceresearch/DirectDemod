'''
noaa commandline interface
'''

from directdemod import source, chunker, comm, constants, filters, fmDemod, sink, amDemod, noaa
import numpy as np
import sys, getopt

# variables to store command line arguments
optlist, args = [], []

# function to display usage statement and exit
def usage(err = ""):
    print(err)
    print("Usage:", sys.argv[0], "[options] <IQ.wav>")
    print("Options:\t-c <Fc in Hz> : centre frequency of the recording")
    print("\t\t-ce : extract centre frequency from file name")
    print("\t\t-f <in Hz> : channel frequencies (in order)")
    print("\t\t-o <str> : output file names (in order)")
    print("\t\t-s <in sample#> : starts of signals (in order)")
    print("\t\t-e <in sample#> : ends of signals (in order)")
    print("\t\t-q : switch I and Q channels")
    print("\t\t-h: print this")
    print()
    print("Defaults:\tThe offset will be picked up from constants.py if there are no -f options")
    print("\t\tif -f option is present, -ce will be enabled if no -c flags present")
    print("\t\toutput filename will be <in_filename>_FM.wav and <in_filename>.png")
    print("\t\tstart and end will be at extremes i.e. full file will be used for decoding")
    print()
    print("Example 1:\tIf you recorded at freq: FC and the signal is at F. Use the command 'python noaa_cli.py -c FC -f F <filename>' to decode the full file.")
    print("Example 2:\tIf you want to decode file from sample S to sample E. Use the command 'python noaa_cli.py -c FC -f F -s S -e E <filename>' to decode the partial file.")
    print("Example 3:\tIf your file has two recordings at F1 and F2. F1 signal is between samples S1 and E1 where as F2 is between S2 and E2. Use the command 'python noaa_cli.py -c FC -f F1 -s S1 -e E1 -f F2 -s S2 -e E2 <filename>' to decode the different channels.")
    exit()

# try to get the arguments, if error occurs display usage
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'c:f:s:e:ho:q', ['help'])
except getopt.GetoptError as e:
    usage(e)

# if args is to get help
if '-h' in [i[0] for i in optlist] or '--help' in [i[0] for i in optlist]:
    usage()

# check if file given
if not (len(args) == 1):
    usage("Invalid argument: filename")

# create the list of frequencies to be decoded
freqs = [int(i[1]) for i in optlist if i[0] == '-f']
starts = [int(i[1]) for i in optlist if i[0] == '-s']
ends = [int(i[1]) for i in optlist if i[0] == '-e']
outs = [i[1] for i in optlist if i[0] == '-o']

# check that starts and ends are less than frequencies
if len(starts) > len(freqs) or len(ends) > len(freqs) or len(outs) > len(freqs):
    usage("number of starts/ends/outfilenames cannot be greater than frequencies given")

# pad with defaults if starts/ends/outfilenames args are less than frequencies given
starts.extend([None]*(len(freqs) - len(starts)))
ends.extend([None]*(len(freqs) - len(ends)))
outs.extend([None]*(len(freqs) - len(outs)))

# if no frequencies given, use default
if len(freqs) == 0:
    freqs = [None]
    starts = [None]
    ends = [None]
    outs = [None]

# input file name
fileName = args[0]

# create this as a signal source
sigsrc = source.IQwav(fileName)

for fileIndex in range(len(freqs)):

    # get the offset
    freqOffset = constants.IQ_FREQOFFSET
    if not freqs[fileIndex] is None: # if a -f is mentioned
        if '-c' in [i[0] for i in optlist if not i[1] == 'e']: # if a -c xxx is mentioned
            freqOffset = freqs[fileIndex] - int([i[1] for i in optlist if (not i[1] == 'e') and i[0] == '-c'][0])
        else: # if -ce is mentioed
            frqFromFileName = [i for i in fileName.split("_") if i[-2:] == "Hz"][0][:-2]
            if frqFromFileName[-1] == "k": # some SDR files have 'k' as in kHz hence need to be multiplied by 1000
                freqOffset = freqs[fileIndex] - (int(frqFromFileName[:-1])*1000)
            else:
                freqOffset = freqs[fileIndex] - int(frqFromFileName)

        # if invertion of IQ is chosen
        if '-q' in [i[0] for i in optlist]:
            freqOffset *= -1

    # output file names
    audFileName = fileName.split(".")[0] + "_FM" + ".wav"
    imgFileName = fileName.split(".")[0] + ".png"
    if not outs[fileIndex] is None:
        audFileName = outs[fileIndex] + ".wav"
        imgFileName = outs[fileIndex] + ".png"

    # limit the source data if start/end is mentioned
    sigsrc.limitData(starts[fileIndex], ends[fileIndex])

    # create noaa object
    noaaObj = noaa.noaa(sigsrc, freqOffset)

    # get the audio
    audioOut = noaaObj.getAudio
    sink.wavFile(audFileName, audioOut).write

    # get the image
    imageMatrix = noaaObj.getImage
    sink.image(imgFileName, imageMatrix).write.show