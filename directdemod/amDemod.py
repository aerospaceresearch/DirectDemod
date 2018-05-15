'''
Object for AM demodulation
'''
import numpy as np
import scipy.signal as signal



class amDemod():
	def __init__(self):
		pass

	def demod(self, sig):
		return np.abs(signal.hilbert(sig))