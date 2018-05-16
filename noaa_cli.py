'''
noaa commandline interface (TEMPORARY)
'''

from directdemod import source, chunker, comm, constants, filters, fmDemod, sink, amDemod
import numpy as np
import sys

'''
TEMP CODE
WILL BE MOVED TO /directdemod/noaa.py
'''

if not (len(sys.argv) == 2):
	print("Usage:", sys.argv[0], "<IQ.wav>")
	exit()

sigsrc = source.IQwav(sys.argv[1])
audioOut = comm.commSignal(constants.NOAA_AUDSAMPRATE)

for i in chunker.chunker(sigsrc).getChunks[:]:
	sig = comm.commSignal(constants.IQ_SDRSAMPRATE, sigsrc.read(*i)).offsetFreq(constants.IQ_FREQOFFSET).filter(filters.blackmanHarris()).bwLim(constants.IQ_FMBW).funcApply(fmDemod.fmDemod().demod).bwLim(constants.NOAA_AUDSAMPRATE, True)
	audioOut.extend(sig)

sink.wavFile("out.wav", audioOut).write

audioOut.updateSignal(audioOut.signal[:constants.NOAA_AUDSAMPRATE*int(audioOut.length // constants.NOAA_AUDSAMPRATE)]).funcApply(amDemod.amDemod().demod).filter(filters.medianFilter())
reshaped = audioOut.signal.reshape(audioOut.length // 5, 5)
(low, high) = np.percentile(reshaped[:, 2], (0.5, 99.5))
delta = high - low
data = np.round(255 * (reshaped[:, 2] - low) / delta)
data[data < 0] = 0
data[data > 255] = 255
digitized = data.astype(np.uint8)
matrix = digitized.reshape((int(len(digitized) / 2080), 2080))

sink.image("out.png", matrix).write.show
