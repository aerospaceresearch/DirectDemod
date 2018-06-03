'''
AFSK1200
'''
from directdemod import source, sink, chunker, comm, constants, filters, demod_am, demod_fm
import numpy as np
import logging
import scipy.signal as signal

'''
Object to decode AFSK1200
'''

class decode_afsk1200:

    '''
    Object to decode AFSK1200
    '''

    def __init__(self, sigsrc, offset, bw):

        '''Initialize the object

        Args:
            sigsrc (:obj:`commSignal`): IQ data source
            offset (:obj:`float`): Frequency offset of source in Hz
            bw (:obj:`int`, optional): Bandwidth
        '''