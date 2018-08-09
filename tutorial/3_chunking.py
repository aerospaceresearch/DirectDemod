'''
A simple tutorial to use chunking
NOTE: All documentation is at directdemod.readthedocs.io

Previous scripts are only good if the input files are small, we will have to chunk the file into
multiple parts if the file is big. This is how its done.

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

# initialize all objects out of loop
sigOut = comm.commSignal(sigsrc.sampFreq)
bhFilter = filters.blackmanHarris(151)
fmDemdulator = demod_fm.demod_fm()
chunkerObj = chunker.chunker(sigsrc)

# use this for loop
for i in chunkerObj.getChunks:
	
	# everything same as previous, but remember to use the same objects, then the continuity will be maintained between the chunks

    sig = comm.commSignal(sigsrc.sampFreq, sigsrc.read(*i), chunkerObj)
    sig.filter(bhFilter)
    sig.bwLim(30000)
    sig.funcApply(fmDemdulator.demod)
    sigOut.extend(sig)

## plot the signal
plt.plot(sigOut.signal)
plt.show()
