'''
noaa commandline interface
'''

from directdemod import source, chunker, comm, constants, filters, fmDemod, sink, amDemod
import numpy as np
import sys

if not (len(sys.argv) == 2):
	print("Usage:", sys.argv[0], "<IQ.wav>")
	exit()

sigsrc = source.IQwav(sys.argv[1])
audioOut = comm.commSignal(sampRate = constants.NOAA_AUDSAMPRATE)

for i in chunker.chunker(sigsrc).getChunks()[:1]:
	sig = comm.commSignal(sigsrc.read(*i))
	sig.offsetFreq(constants.IQ_FREQOFFSET)
	sig.filter(filters.blackmanHarris())
	sig.bwLim(constants.IQ_FMBW)
	sig.funcApply(fmDemod.fmDemod().demod)
	sig.bwLim(constants.NOAA_AUDSAMPRATE, True)
	audioOut.extend(sig)

sink.wavFile("out.wav").write(audioOut)

audioOut.updateSignal(audioOut.signal[:constants.NOAA_AUDSAMPRATE*int(audioOut.length // constants.NOAA_AUDSAMPRATE)])
audioOut.funcApply(amDemod.amDemod().demod);
audioOut.filter(filters.medianFilter())

reshaped = audioOut.signal.reshape(audioOut.length // 5, 5)

# get high low values to quantise
(low, high) = np.percentile(reshaped[:, 2], (0.5, 99.5))
delta = high - low

# quantize pixels
data = np.round(255 * (reshaped[:, 2] - low) / delta)
data[data < 0] = 0
data[data > 255] = 255
digitized = data.astype(np.uint8)
matrix = digitized.reshape((int(len(digitized) / 2080), 2080))

sink.image("out.png").show(matrix)
