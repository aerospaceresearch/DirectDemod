'''
Object for filters
'''
import scipy.signal as signal

class blackmanHarris:
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
