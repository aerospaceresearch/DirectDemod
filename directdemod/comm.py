'''
Signal utilities
'''

import directdemod.constants as constants
import numpy as np
import scipy.signal as signal


'''
This is an object used to store a signal and its properties
e.g. To use this to store a audio signal: audioSig = commSignal(ArrayWithSignalValues, SamplingRate)
Refer: Experiment 1 for testing memory effeciency of the object
'''

class commSignal:
	'''
	# Description: Initialize the object
	# NecessaryInputs: sampRate (in Hz, will be forced to be an integer)
	# OptionalInputs: sig (must be one dimentional, will be forced to be a numpy array)
	# Outputs: -
	'''
	def __init__(self, sampRate, sig = np.array([])):
		self.__len = len(sig)

		self.__sampRate = int(sampRate)
		if self.__sampRate <= 0:
			raise ValueError("The sampling rate must be greater than zero")

		self.__sig = np.array(sig)
		if not self.__sig.size == self.__sig.shape[0]:
			raise TypeError("The signal array must be 1-D")

	'''
	# Description: get length of signal
	# Inputs: -, Outputs: length of signal
	'''
	@property
	def length(self):
		return self.__len

	'''
	# Description: get sampling rate of signal
	# Inputs: -, Outputs: sampling rate of signal
	'''
	@property
	def sampRate(self):
		return self.__sampRate

	'''
	# Description: get signal
	# Inputs: -, Outputs: current signal
	'''
	@property
	def signal(self):
		return self.__sig

	'''
	# Description: offset signal frequency by multiplying a complex envelope
	# Inputs: freqOffset (in Hz), Outputs: self
	'''
	def offsetFreq(self, freqOffset):
		self.__sig *= np.exp(-1.0j*2.0*np.pi*freqOffset*np.arange(self.length)/self.sampRate)
		return self

	'''
	# Description: apply a filter to the signal
	# Inputs: filter object, Outputs: self
	'''
	def filter(self, filt):
		self.updateSignal(filt.applyOn(self.signal))
		return self

	'''
	# Description: limit the bandwidth by downsampling
	# Inputs: tsampRate (target sample rate), strictness (if true, the target sample rate will be matched exactly)
	# Outputs: self
	'''
	def bwLim(self, tsampRate, strict = False):
		if self.__sampRate < tsampRate:
			raise ValueError("The target sampling rate must be less than current sampling rate")

		if strict:
			self.__sig = signal.resample(self.signal, int(tsampRate * self.length/self.sampRate))
			self.__sampRate = tsampRate
			self.__len = len(self.signal)
		else:
			jumpIndex = int(self.sampRate / tsampRate)
			self.__sig = self.signal[0::jumpIndex]
			self.__sampRate = int(self.sampRate/jumpIndex)
			self.__len = len(self.signal)
		return self

	'''
	# Description: applys a function to the signal
	# Inputs: function to be applied, Outputs: self
	'''
	def funcApply(self, func):
		self.updateSignal(func(self.signal))
		return self

	'''
	# Description: Adds another signal to this one
	# Inputs: commSignal object, Outputs: self
	'''
	def extend(self, sig):
		if not self.__sampRate == sig.sampRate:
			raise TypeError("Signals must have same sampling rate to be extended")
		
		self.updateSignal(np.concatenate([self.signal, sig.signal]))
		return self

	'''
	# Description: Updates the signal
	# Inputs: sig array, Outputs: self
	'''
	def updateSignal(self, sig):
		self.__sig = np.array(sig)
		if not self.__sig.size <= self.__sig.shape[0]:
			raise TypeError("The signal array must be 1-D")
		self.__len = len(self.signal)
		return self