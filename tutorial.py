'''
A simple tutorial program to FM demodulate an APRS IQ.wav file
NOTE: All documentation is at directdemod.readthedocs.io
'''

# Import all modules
from directdemod import source, sink, chunker, comm, constants, filters, demod_am, demod_fm
import matplotlib.pyplot as plt

## First the source of data
fileName = "samples/SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav"
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

## Apply a blackman harris filter to get rid of noise
bhFilter = filters.blackmanHarris(151)
sig.filter(bhFilter)

## Limit bandwidth, say 30000
sig.bwLim(30000)

## FM demodulate
fmDemodulator = demod_fm.demod_fm()
sig.funcApply(fmDemodulator.demod)

## APRS has two freqs 1200 and 2200, hence create a butter band pass filter from 1200-500 to 2200+500
bFilter = filters.butter(sig.sampRate, 1200-500, 2200+500, typeFlt = constants.FLT_BP)
sig.filter(bFilter)

## plot the signal
plt.plot(sig.signal)
plt.show()