'''
A source is any input data source.
Say a IQ.wav file
'''

from abc import ABCMeta, abstractmethod
import directdemod.constants as constants
import numpy as np

'''
Abstract model of a class, to keep the models consistent
Any source must inherit this abstract class
The general structure is as follows
'''

'''
class source(metaclass=ABCMeta):
	### Properties

	# A source type variable (different types defined in constant.py)
	@property
	def sourceType(self):
		raise NotImplementedError

	# The source sampling frequency
	@property
	def sampFreq(self):
		raise NotImplementedError

	# The source data length
	@property
	def lengths(self):
		raise NotImplementedError

	### Methods

	# Constructor: Source specific
	# Description: Initialize the object
	# NecessaryInputs: -
	# OptionalInputs: -
	# Outputs: -
	def __init__(self):
		pass

	# Every source must have a read method
	# Description: read values from 'fromIndex' to 'toIndex'
	# NecessaryInputs: fromIndex
	# OptionalInputs: toIndex
	@abstractmethod
	def read(self, fromIndex, toIndex):
		pass

	# Destructor: Source specific
	# Description: Delete unnecessary objects to free up space
	# NecessaryInputs: -
	# OptionalInputs: -
	# Outputs: -
	def __del__(self):
		pass
'''

'''
An IQ.wav file source, typically an output recorded from SDRSHARP
The IQ wav file contains two channels, one channel for I component and the other for Q
'''
class IQwav:
	def __init__(self, filename):
		sourceType = constants.SOURCE_IQWAV
		self.__data = np.memmap(filename, offset=44)
		self.length = int(len(self.__data)/2)

	def read(self, fromIndex, toIndex = None):
		if toIndex == None:
			toIndex = fromIndex + 1
		samples = (self.__data[2*fromIndex:2*toIndex:2]) + 1j * (self.__data[1+2*fromIndex:1+2*toIndex:2])
		return np.array(samples).astype("complex64") - (129 + 1j*129)