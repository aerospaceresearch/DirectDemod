'''
Object for FM demodulation
'''
import numpy as np
import scipy.signal as signal

class fmDemod():
	def __init__(self):
		pass

	def demod(self, sig):
		sig_fmd = sig[1:] * np.conj(sig[:-1])  
		return np.angle(sig_fmd)