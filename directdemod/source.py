'''
A source is any input data source.
Say a IQ.wav file
'''

from abc import ABCMeta, abstractmethod
import directdemod.constants as constants
import numpy as np
import scipy.io.wavfile

'''
Abstract model of a class, to keep the models consistent
Any source must inherit this abstract class
The general structure is as follows
The goal of having such a parent abstract class is that, the children are forced to implement the required methods
'''

class source(metaclass=ABCMeta):
	### Properties

	# A source type variable (different types defined in constant.py)
	@property
	@abstractmethod
	def sourceType(self):
		pass

	# The source sampling frequency
	@property
	@abstractmethod
	def sampFreq(self):
		pass

	# The source data length
	@property
	@abstractmethod
	def length(self):
		pass

	### Methods

	# Every source must have a read method
	# Description: read values from 'fromIndex' to 'toIndex'
	# NecessaryInputs: fromIndex
	# OptionalInputs: toIndex
	@abstractmethod
	def read(self, fromIndex, toIndex):
		pass

'''
An IQ.wav file source, typically an output recorded from SDRSHARP
The IQ wav file contains two channels, one channel for I component and the other for Q
'''
class IQwav(source):
	'''
	# Description: Initialize the object
	# Inputs: filename of the IQ.wav file
	# Outputs: -
	'''
	def __init__(self, filename):
		self.__sourceType = constants.SOURCE_IQWAV
		self.__sampFreq, self.__data = scipy.io.wavfile.read(filename, True)
		self.__length = self.__data.shape[0]

	# Description: get sampling freq of source
	# Inputs: -, Outputs: sampling freq of source
	@property
	def sampFreq(self):
		return self.__sampFreq

	# Description: get source type
	# Inputs: -, Outputs: get source type
	@property
	def sourceType(self):
		return self.__sourceType

	# Description: get source length
	# Inputs: -, Outputs: get source length
	@property
	def length(self):
		return self.__length

	# Read source data
	# Description: read values from 'fromIndex' to 'toIndex'
	# NecessaryInputs: fromIndex
	# OptionalInputs: toIndex
	def read(self, fromIndex, toIndex = None):
		if toIndex == None:
			toIndex = fromIndex + 1

		if fromIndex < 0 or toIndex < 0 or fromIndex >= self.__length or toIndex > self.__length:
			raise ValueError("fromIndex and toIndex have invalid values")

		samples = self.__data[fromIndex:toIndex,0] + 1j * self.__data[fromIndex:toIndex,1]
		return np.array(samples).astype("complex64") - (127.5 + 1j*127.5)

'''
Note: This is an alternative implementation, directly using np.memmap
An IQ.wav file source, typically an output recorded from SDRSHARP
The IQ wav file contains two channels, one channel for I component and the other for Q
'''
class IQwavAlt(source):
	'''
	# Description: Initialize the object
	# Inputs: filename of the IQ.wav file
	# Outputs: -
	'''
	def __init__(self, filename):
		self.__sourceType = constants.SOURCE_IQWAV
		self.__data = np.memmap(filename, offset=44)
		self.__length = int(len(self.__data)/2)
		self.__sampFreq = constants.IQ_SDRSAMPRATE

	# Description: get sampling freq of source
	# Inputs: -, Outputs: sampling freq of source
	@property
	def sampFreq(self):
		return self.__sampFreq

	# Description: get source type
	# Inputs: -, Outputs: get source type
	@property
	def sourceType(self):
		return self.__sourceType

	# Description: get source length
	# Inputs: -, Outputs: get source length
	@property
	def length(self):
		return self.__length

	# Read source data
	# Description: read values from 'fromIndex' to 'toIndex'
	# NecessaryInputs: fromIndex
	# OptionalInputs: toIndex
	def read(self, fromIndex, toIndex = None):
		if toIndex == None:
			toIndex = fromIndex + 1

		if fromIndex < 0 or toIndex < 0 or fromIndex >= self.__length or toIndex > self.__length:
			raise ValueError("fromIndex and toIndex have invalid values")
			
		samples = (self.__data[2*fromIndex:2*toIndex:2]) + 1j * (self.__data[1+2*fromIndex:1+2*toIndex:2])
		return np.array(samples).astype("complex64") - (127.5 + 1j*127.5)