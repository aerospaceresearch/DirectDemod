'''
Object for AM demodulation
'''
import numpy as np
import scipy.signal as signal

'''
AM demodulation by hilbert's transform
'''

class amDemod():
    def demod(self, sig):

        '''AM demodulation by hilbert's transform
        
        Args:
            sig (:obj:`numpy array`): Signal array to be demdodulated

        Returns:
            :obj:`numpy array`: Demodulated signal
        '''

        return np.abs(signal.hilbert(sig))