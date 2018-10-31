'''
A simple tutorial program to FM demodulate an APRS IQ.wav file
NOTE: All documentation is at directdemod.readthedocs.io

A simple FM demodulator would be a good start for us.
Record a sample IQ.wav file from your RTLSDR or use the one provided in the samples flder.

'''

# Firstly we will have to import whatever libraries we would need
import os, sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)

from directdemod import source, comm, demod_fm
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

## Limit bandwidth, say 30000
sig.bwLim(30000)

## FM demodulate
fmDemodulator = demod_fm.demod_fm()
sig.funcApply(fmDemodulator.demod)

## plot the signal
plt.plot(sig.signal)
plt.show()

# Hmmm.. we dont see any signal, maybe because of lack of filters, so next we apply some filters to get a better result.