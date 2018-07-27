'''
noaa commandline interface
'''

from directdemod import source, chunker, comm, constants, filters, demod_fm, sink, demod_am, decode_noaa, log, decode_afsk1200, decode_funcube, decode_meteorm2
import numpy as np
import sys, getopt, logging, json
from time import gmtime, strftime
from datetime import datetime

# enable logging to console
log.log('log.txt', console = True)

# variables to store command line arguments
optlist, args = [], []

# function to display usage statement and exit
def usage(err = ""):
    if len(err) > 0:
        print("ERROR :",err)

    # common to all decoders
    print("Usage:", sys.argv[0], "[options] <IQ.wav>")
    print()
    print("Common options:")
    print("\t-c <Fc in Hz> : centre frequency of the recording")
    print("\t-ce : extract centre frequency from file name")
    print("\t-a <F in Hz> : sampling frequency of the recording")
    print("\t-q : switch I and Q channels")
    print("\t-r <filename> : generate report in JSON")
    print("\t-h : print this")
    print()
    print("Channels:")
    print("\t-f <in Hz> : For every channel add a -f flag with respective frequency")
    print("\tOptions for each channel: (if set, must follow -f of the respective channel)")
    print("\t\t-d <str> : decoder for this channel, look below for list of decoders (in order)")
    print("\t\t-b <in Hz> : channel  bandwidth (in order)")
    print("\t\t-o <str> : output file names (in order)")
    print("\t\t-s <in sample#> : starts of signals (in order)")
    print("\t\t-e <in sample#> : ends of signals (in order)")
    
    print()
    print("for each -f channel use following flags to indicate which decoder to use:")
    print("\t-d noaa : APT e.g. NOAA satellites decoder")
    print("\t\tNOAA specifc flags:")
    print("\t\t-sync : calculate sync values and store in .csv file")
    print("\t\t--map : generates map overlay")
    print("\t\t--tle=<filename> : TLE source filename")
    print("\t\t-noimage : doesn't show/store image")
    print("\t-d afsk1200 : AFSK1200 decoder")
    print("\t-d funcube : Funcube BPSK sync detector")
    print("\t-d meteor : Meteor QPSK sync detector")
    print()
    exit()

# try to get the arguments, if error occurs display usage
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'c:f:s:e:ho:qn:b:d:r:a:', ['help', 'map', 'tle='])
except getopt.GetoptError as e:
    usage(e)

# if args is to get help
if '-h' in [i[0] for i in optlist] or '--help' in [i[0] for i in optlist]:
    usage()

# show map
mapDraw = False# if args is to get help
if '--map' in [i[0] for i in optlist]:
    mapDraw = True

# check if file given
if not (len(args) == 1):
    usage("Invalid argument: filename")

# check is -sync flag is set
calculateSync = False
if len([i for i in optlist if (i[0] == '-s' and i[1] == 'ync')]) > 0:
    calculateSync = True

# check is -noimage flag is set
calculateImage = True
if len([i for i in optlist if (i[0] == '-n' and i[1] == 'oimage')]) > 0:
    calculateImage = False

# check if -r is set to generate report
reportFile = None
if len([i for i in optlist if i[0] == '-r']) > 0:
    reportFile = [i[1] for i in optlist if i[0] == '-r'][0]

# check if -a is set to get sampling rate
givenSampRate = None
if len([i for i in optlist if i[0] == '-a']) > 0:
    givenSampRate = int([i[1] for i in optlist if i[0] == '-a'][0])

# create the list of frequencies to be decoded
freqs = [int(i[1]) for i in optlist if i[0] == '-f']
starts = [int(i[1]) for i in optlist if i[0] == '-s' and not i[1] == 'ync']
ends = [int(i[1]) for i in optlist if i[0] == '-e']
outs = [i[1] for i in optlist if i[0] == '-o']
bandwidths = [int(i[1]) for i in optlist if i[0] == '-b']
decoders = [i[1] for i in optlist if i[0] == '-d']

# if no frequencies given, use default
if len(freqs) == 0:
    freqs = [None]

# check that number of decoders is equal to channels
if not len(freqs) == len(decoders):
    usage("Every -f channel must be accompanied by a decoder")

# check that starts and ends are less than frequencies
if len(starts) > len(freqs) or len(ends) > len(freqs) or len(outs) > len(freqs) or len(bandwidths) > len(freqs):
    usage("number of starts/ends/outfilenames cannot be greater than frequencies given")

# pad with defaults if starts/ends/outfilenames args are less than frequencies given
starts.extend([None]*(len(freqs) - len(starts)))
ends.extend([None]*(len(freqs) - len(ends)))
outs.extend([None]*(len(freqs) - len(outs)))
bandwidths.extend([None]*(len(freqs) - len(bandwidths)))

# input file name
fileName = args[0]

# create this as a signal source
sigsrc = None
if fileName[-3:] == "wav":
    sigsrc = source.IQwav(fileName, givenSampRate)
elif fileName[-3:] == "dat":
    sigsrc = source.IQdat(fileName, givenSampRate)
else:
    usage("Only .wav and .dat files are supported")

# report dictionary
reportDict = {}
reportDict['inFileName'] = fileName
reportDict['timeOfExec'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
reportDict['invIQ'] = '-q' in [i[0] for i in optlist]
reportDict['channels'] = []

for fileIndex in range(len(freqs)):
    try:
        # add entry to report
        entryDict = {}
        entryDict['frequency'] = freqs[fileIndex]
        entryDict['bandwidth'] = bandwidths[fileIndex]
        entryDict['decoder'] = decoders[fileIndex]
        entryDict['startFlag'] = starts[fileIndex]
        entryDict['endFlag'] = ends[fileIndex]
        entryDict['outFileName'] = outs[fileIndex]

        logging.info('Beginning decoding of frequency %d of %d frequencies', fileIndex+1, len(freqs))

        # get the offset
        freqOffset = constants.IQ_FREQOFFSET
        if not freqs[fileIndex] is None: # if a -f is mentioned
            if '-c' in [i[0] for i in optlist if not i[1] == 'e']: # if a -c xxx is mentioned
                freqOffset = freqs[fileIndex] - int([i[1] for i in optlist if (not i[1] == 'e') and i[0] == '-c'][0])
                reportDict['centreFreq'] = [i[1] for i in optlist if i[0] == '-c'][0]
            else: # if -ce is mentioed
                frqFromFileName = [i for i in fileName.split("_") if i[-2:] == "Hz"][0][:-2]
                if frqFromFileName[-1] == "k": # some SDR files have 'k' as in kHz hence need to be multiplied by 1000
                    freqOffset = freqs[fileIndex] - (int(frqFromFileName[:-1])*1000)
                    reportDict['centreFreq'] = (int(frqFromFileName[:-1])*1000)
                else:
                    freqOffset = freqs[fileIndex] - int(frqFromFileName)
                    reportDict['centreFreq'] = int(frqFromFileName)

        # if invertion of IQ is chosen
        if '-q' in [i[0] for i in optlist]:
            freqOffset *= -1

        entryDict['offset'] = freqOffset

        logging.info('Offset for this frequency was determined to be %f Hz', freqOffset)

        # limit the source data if start/end is mentioned
        sigsrc.limitData(starts[fileIndex], ends[fileIndex])

        ## If NOAA was chosen
        if decoders[fileIndex] == "noaa":
            logging.info('Decoding NOAA data')

            entryDict['filesCreated'] = []

            # output file names
            audFileName = fileName.split(".")[0] + "_FM" + "_f" + str(fileIndex+1) + ".wav"
            imgFileName = fileName.split(".")[0] + "_f" + str(fileIndex+1) + ".png"
            colorimgFileName = fileName.split(".")[0] + "_f" + str(fileIndex+1) + "_color.png"
            csvFileName = fileName.split(".")[0] + "_f" + str(fileIndex+1) + ".csv"
            mapImageFileNameRot = fileName.split(".")[0] + "_f" + str(fileIndex+1) + "_map_rot.png"
            mapImageFileNameNRot = fileName.split(".")[0] + "_f" + str(fileIndex+1) + "_map.png"
            if not outs[fileIndex] is None:
                audFileName = outs[fileIndex] + ".wav"
                imgFileName = outs[fileIndex] + ".png"
                csvFileName = outs[fileIndex] + ".csv"
                colorimgFileName = outs[fileIndex] + "_color.png"
                mapImageFileNameRot = outs[fileIndex] + "_map_rot.png"
                mapImageFileNameNRot = outs[fileIndex] + "_map.png"

            # create noaa object
            noaaObj = decode_noaa.decode_noaa(sigsrc, freqOffset, bandwidths[fileIndex])

            # get the image if -noimage is not present
            if calculateImage and noaaObj.useful == 1:
                # get the audio
                #audioOut = noaaObj.getAudio
                #sink.wavFile(audFileName, audioOut).write
                #entryDict['filesCreated'].append(audFileName)

                imageMatrix = noaaObj.getImage
                sink.image(imgFileName, imageMatrix).write
                entryDict['filesCreated'].append(imgFileName)

                if not noaaObj.channelID[0] is None and not noaaObj.channelID[1] is None:
                    logging.info('NOAA image has channel A id: %d and channel B id: %d', noaaObj.channelID[0], noaaObj.channelID[1])

                # Experimental
                if noaaObj.channelID[0] == 2 and noaaObj.channelID[1] == 4:
                    logging.info('Writing false color image')
                    sink.image(colorimgFileName, noaaObj.getColor).write
                    entryDict['filesCreated'].append(colorimgFileName)
                else:
                    logging.info('This image is ineligible to be converted to false color')

                # Experimental: map overlay
                if mapDraw:
                    satName = None
                    try:
                        satName = constants.NOAA_SATS[freqs[fileIndex]]
                        logging.info("The satellite was found to be %s", satName)
                    except:
                        logging.error("This satellite frequency not found")

                    timeRec = None
                    try:
                        dateRecT, timeRecT = None, None
                        fnameParts = fileName.split("_")[::-1]
                        for i in range(len(fnameParts)):
                            if fnameParts[i][-1] == "Z":
                                dateRecT = fnameParts[i+1]
                                timeRecT = fnameParts[i][:-1]
                        if dateRecT is None or timeRecT is None:
                            raise Exception("Invalid file name format")

                        logging.info("Time of recording was determined to be: date: %s time: %s", dateRecT, timeRecT)

                        timeRec = datetime(int(dateRecT[:4]), int(dateRecT[4:6]), int(dateRecT[6:8]), int(timeRecT[:2]), int(timeRecT[2:4]), int(timeRecT[4:6]))
                    except:
                        logging.error("Was not able to get time from file name")

                    tleFileName = None
                    if '--tle' in [i[0] for i in optlist]:
                        tleFileName = [i[1] for i in optlist if i[0] == '--tle'][0]

                    if not satName is None and not timeRec is None:
                        imageMatrix = noaaObj.getMapImage(timeRec, mapImageFileNameRot, mapImageFileNameNRot, satName, tleFileName)
                        entryDict['filesCreated'].append(mapImageFileNameRot)
                        entryDict['filesCreated'].append(mapImageFileNameNRot)

            # calculate sync is -sync flag is set
            if calculateSync and noaaObj.useful == 1:
                syncs = noaaObj.getAccurateSync(useNormCorrelate = True) # change to False to use scipy's correlate
                sink.csv(csvFileName, syncs, titles = ["syncA", "diffSyncA", "qualityA", "TimeSyncA", "syncB", "diffSyncB", "qualityB", "TimeSyncB",]).write
                entryDict['filesCreated'].append(csvFileName)

            if noaaObj.useful == 0:
                logging.info('No NOAA data was found at this frequency')

            entryDict['usefulness'] = noaaObj.useful
            entryDict['syncDetect'] = calculateSync
            entryDict['image'] = calculateImage

        # if AFSK1200 was chosen
        elif decoders[fileIndex] == "afsk1200":
            logging.info('Decoding AFSK1200 data')

            entryDict['filesCreated'] = []

            # create AFSK1200 object
            afskObj = decode_afsk1200.decode_afsk1200(sigsrc, freqOffset, bandwidths[fileIndex])
            print(afskObj.getMsg)

            entryDict['usefulness'] = afskObj.useful

        # if Funcube BPSK was chosen
        elif decoders[fileIndex] == "funcube":
            logging.info('Detecting Funcube Syncs')

            entryDict['filesCreated'] = []

            # create funcube object
            funcubeObj = decode_funcube.decode_funcube(sigsrc, freqOffset, bandwidths[fileIndex])
            syncs = funcubeObj.getSyncs

            #print results
            logging.info('Complete: detected %d syncs', len(syncs))
            
            # write syncs
            csvFileName = fileName.split(".")[0] + "_f" + str(fileIndex+1) + ".csv"
            if not outs[fileIndex] is None:
                csvFileName = outs[fileIndex] + ".csv"

            sink.csv(csvFileName, [syncs], titles = ["Funcube syncs"]).write
            entryDict['filesCreated'].append(csvFileName)

            logging.info('CSV file successfully created')

            entryDict['usefulness'] = funcubeObj.useful
        
        # if Meteor m2 QPSK was chosen
        elif decoders[fileIndex] == "meteor":
            logging.info('Detecting Meteor M2 Syncs')

            entryDict['filesCreated'] = []

            # create meteor object
            meteorObj = decode_meteorm2.decode_meteorm2(sigsrc, freqOffset, bandwidths[fileIndex])
            syncs = meteorObj.getSyncs

            #print results
            logging.info('Complete: detected %d syncs', len(syncs))
            
            # write syncs
            csvFileName = fileName.split(".")[0] + "_f" + str(fileIndex+1) + ".csv"
            if not outs[fileIndex] is None:
                csvFileName = outs[fileIndex] + ".csv"

            sink.csv(csvFileName, [syncs], titles = ["Meteor syncs"]).write
            entryDict['filesCreated'].append(csvFileName)

            logging.info('CSV file successfully created')

            entryDict['usefulness'] = meteorObj.useful

        else:
            usage("Invalid decoder selected")


        reportDict['channels'].append(entryDict)
    except Exception as e:
        logging.error('An error occured during decoding of frequency %d of %d frequencies', fileIndex+1, len(freqs))
        logging.error('The error is: %s', str(e))

# write report
if not reportFile is None:
    with open(reportFile, 'w') as outfile:
        json.dump(reportDict, outfile)