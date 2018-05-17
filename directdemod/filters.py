'''
Object for filters
'''

import scipy.signal as signal

'''
Abstract model of a class, to keep the models consistent
Any filter must inherit this abstract class
The general structure is as follows
The goal of having such a parent abstract class is that, the children are forced to implement the required methods
'''

class filter:

	'''
	This is a parent object of all filters, it implements all the necessary properties. Refer to experiment 3 for details.
	'''

	def __init__(self, b, a, storeState = True, zeroPhase = False, initOut = None):

		'''Initialize the object

	    Args:
	    	b (:obj:`list`): list of 'b' constants of filter
	    	a (:obj:`list`): list of 'a' constants of filter
	        storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
	        zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
	        initOut (:obj:`list`, optional): Initial condition of the filter

	    '''

		self.__storeState = storeState
		self.__zeroPhase = zeroPhase
		self.__initOut = initOut

		if self.__storeState  and self.__zeroPhase:
			self.__storeState = False

		if (not self.__initOut == None) and self.__zeroPhase:
			self.__initOut = None

		if self.__storeState:
			self.__zi = signal.lfilter_zi(b, a)

		if not self.__initOut == None:
			self.__zi = None

		self.__b = b
		self.__a = a

	def applyOn(self, x):

		'''Apply the filter to a given array of signal

	    Args:
	        x (:obj:`numpy array`): The signal array on which the filter needs to be applied

	    Returns:
	        :obj:`numpy array`: Filtered signal array
	    '''

		if self.__storeState:

			if self.__zi is None:
				self.__zi = signal.lfiltic(self.__b, self.__a, x, self.__initOut)

			retDat, self.__zi = signal.lfilter(self.__b, self.__a, x, zi=self.__zi)
			return retDat
		else:
			if self.__zeroPhase:
				return signal.filtfilt(self.__b, self.__a, x)
			else:
				return signal.lfilter(self.__b, self.__a, x)

'''
A simple rolling average filter
'''

class rollingAverage(filter):

	'''
	A simple rolling average filter
	'''

	def __init__(self, n = 3, storeState = True, zeroPhase = False, initOut = None):

		'''Initialize the object

	    Args:
	    	n (:obj:`int`, optional): size of the rolling window
	        storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
	        zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
	        initOut (:obj:`list`, optional): Initial condition of the filter

	    '''

		self.__n = n
		super(rollingAverage, self).__init__([1.0/n]*n, [1], storeState, zeroPhase, initOut)

'''
To be implemented later
'''

class blackmanHarris(filter):
	def __init__(self, n = 151, storeState = True):
		self.__n = n
		super(blackmanHarris, self).__init__(signal.blackmanharris(self.__n), [1], storeState)

class blackmanHarrisConv:
	def __init__(self, n = 151):
		self.__n = n
		self.__window = signal.blackmanharris(self.__n)

	def applyOn(self, sig):
		return signal.convolve(sig, self.__window, mode='same')

class medianFilter:
	def __init__(self, n = 5):
		self.__n = n
	def applyOn(self, sig):
		return signal.medfilt(sig, self.__n)

	