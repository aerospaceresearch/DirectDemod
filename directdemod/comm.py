'''
Object for signal utilities
'''
import directdemod.constants as constants
import numpy as np
import scipy.signal as signal

class commSignal:
	def __init__(self, sig = np.array([]), sampRate = constants.IQ_SDRSAMPRATE):
		self.length = len(sig)
		self.sampRate = int(sampRate)
		self.signal = sig

	def offsetFreq(self, freqOffset):
		self.signal *= np.exp(-1.0j*2.0*np.pi*freqOffset*np.arange(self.length)/self.sampRate)

	def filter(self, filt):
		self.updateSignal(filt.applyOn(self.signal))

	def bwLim(self, tsampRate, strict = False):
		if strict:
			self.signal = signal.resample(self.signal, int(tsampRate * self.length/self.sampRate))
			self.sampRate = int(tsampRate * self.length/self.sampRate)
			self.length = len(self.signal)
		else:
			jumpIndex = int(self.sampRate / tsampRate)  
			self.signal = self.signal[0::jumpIndex]
			self.sampRate = int(self.sampRate/jumpIndex)
			self.length = len(self.signal)

	def funcApply(self, func):
		self.updateSignal(func(self.signal))

	def extend(self, sig):
		self.updateSignal(np.concatenate([self.signal, sig.signal]))

	def updateSignal(self, sig):
		self.signal = sig
		self.length = len(self.signal)