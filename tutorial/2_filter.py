'''
A simple tutorial to use filters
NOTE: All documentation is at directdemod.readthedocs.io

A simple FM demodulator would be a good start for us.
Record a sample IQ.wav file from your RTLSDR or use the one provided in the samples flder.

'''

# Firstly we will have to import whatever libraries we would need
import os, sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)
    
from directdemod import source, sink, chunker, comm, constants, filters, demod_am, demod_fm
import matplotlib.pyplot as plt

## First the source of data
fileName = "../samples/SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav"
sigsrc = source.IQwav(fileName)

## Next create a signal object, reading data from the source
# Read all values from the source into an array
sigArray = sigsrc.read(0, sigsrc.length)

# a commSignal object basically stores the signal array and its samplingrate
# if you want the array do sig.signal
# if you want the samping rate do sig.sampRate
sig = comm.commSignal(sigsrc.sampFreq, sigArray)

## Offset the frequency if required, not needed here
# sig.offsetFreq(0)

########### Apply a blackman harris filter to get rid of noise
bhFilter = filters.blackmanHarris(151)
sig.filter(bhFilter)

## Limit bandwidth, say 30000
sig.bwLim(30000)

## FM demodulate
fmDemodulator = demod_fm.demod_fm()
sig.funcApply(fmDemodulator.demod)

########### APRS has two freqs 1200 and 2200, hence create a butter band pass filter from 1200-1000 to 2200+1000
bFilter = filters.butter(sig.sampRate, 1200-1000, 2200+1000, typeFlt = constants.FLT_BP)
sig.filter(bFilter)

## plot the signal
plt.plot(sig.signal)
plt.show()

#### We can clearly see that the filters provide a way better result