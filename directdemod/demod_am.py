'''
Object for AM demodulation
'''
import numpy as np
import scipy.signal as signal
from directdemod import filters, constants

'''
AM demodulation by hilbert's transform
'''

class demod_am():

    '''
    AM demodulation by hilbert's transform
    '''

    def demod(self, sig):

        '''AM demodulation by hilbert's transform
        
        Args:
            sig (:obj:`numpy array`): Signal array to be demdodulated

        Returns:
            :obj:`numpy array`: Demodulated signal
        '''

        return np.abs(signal.hilbert(sig))

'''
AM demodulation by low pass filter
'''

class demod_amFLT():

    '''
    AM demodulation by low pass filter
    '''

    def __init__(self, Fs, cutoff):

        '''Initialize the object

        Args:
            cutoff (:obj:`int`): lowpass cutoff frequency in Hz
        '''

        self.__filter = filters.butter(Fs, cutoff)

    def demod(self, sig):

        '''AM demodulation by low pass filter
        
        Args:
            sig (:obj:`numpy array`): Signal array to be demdodulated

        Returns:
            :obj:`numpy array`: Demodulated signal
        '''

        return self.__filter.applyOn(np.abs(sig))