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
    This is an object used to store a signal and its properties
    '''

    def __init__(self, sampRate, sig = np.array([]), chunker = None):

        '''Initialize the object

        Args:
            sampRate (:obj:`int`): sampling rate in Hz, will be forced to be an integer
            sig (:obj:`numpy array`, optional): must be one dimentional, will be forced to be a numpy array
            chunker (:obj:`chunker`, optional): Chunking object, if this signal is going to be processed in chunks
        '''
        self.__chunker = chunker

        self.__len = len(sig)

        self.__sampRate = int(sampRate)
        if self.__sampRate <= 0:
            raise ValueError("The sampling rate must be greater than zero")

        self.__sig = np.array(sig)
        if not self.__sig.size == self.__sig.shape[0]:
            raise TypeError("The signal array must be 1-D")

    @property
    def length(self):

        ''':obj:`int`: get length of signal'''

        return self.__len

    @property
    def sampRate(self):

        ''':obj:`int`: get sampling rate of signal'''

        return self.__sampRate

    @property
    def signal(self):

        ''':obj:`numpy array`: get signal'''

        return self.__sig

    def offsetFreq(self, freqOffset):

        '''Offset signal by a frequency by multiplying a complex envelope

        Args:
            freqOffset (:obj:`float`): offset frequency in Hz

        Returns:
            :obj:`commSignal`: Signal offset by given frequency (self)
        '''
        offset = 0
        if not self.__chunker is None:
            offset = self.__chunker.get(constants.CHUNK_FREQOFFSET, 0)
            self.__chunker.set(constants.CHUNK_FREQOFFSET, offset + self.length)
        self.__sig *= np.exp(-1.0j*2.0*np.pi*freqOffset*np.arange(offset, offset + self.length)/self.sampRate)
        return self

    def filter(self, filt):

        '''Apply a filter to the signal

        Args:
            filt (:obj:`filter`): filter object

        Returns:
            :obj:`commSignal`: Updated signal (self)
        '''

        self.updateSignal(filt.applyOn(self.signal))
        return self

    def bwLim(self, tsampRate, strict = False, uniq = "abcd"):

        '''Limit the bandwidth by downsampling

        Args:
            tsampRate (:obj:`int`): target sample rate
            strict (:obj:`bool`, optional): if true, the target sample rate will be matched exactly
            uniq (:obj:`str`, optional): in case chunked signal, uniq is to differentiate different bwLim funcs

        Returns:
            :obj:`commSignal`: Updated signal (self)
        '''

        if self.__sampRate < tsampRate:
            raise ValueError("The target sampling rate must be less than current sampling rate")

        if strict:

            # will be depreciated later on, try not to use

            self.__sig = signal.resample(self.signal, int(tsampRate * self.length/self.sampRate))
            self.__sampRate = tsampRate
            self.__len = len(self.signal)

        else:
            jumpIndex = int(self.sampRate / tsampRate)

            offset = 0
            if not self.__chunker is None:
                offset = self.__chunker.get(constants.CHUNK_BWLIM + uniq, 0)
                nextOff = (jumpIndex - (self.length - offset)%jumpIndex)%jumpIndex
                self.__chunker.set(constants.CHUNK_BWLIM + uniq, nextOff)

            self.__sig = self.signal[offset::jumpIndex]
            self.__sampRate = int(self.sampRate/jumpIndex)
            self.__len = len(self.signal)
        return self

    def funcApply(self, func):

        ''' Applies a function to the signal

        Args:
            func (function): function to be applied

        Returns:
            :obj:`commSignal`: Updated signal (self)
        '''

        self.updateSignal(func(self.signal))
        return self

    def extend(self, sig):

        ''' Adds another signal to this one at the tail end

        Args:
            sig (:obj:`commSignal`): Signal to be added

        Returns:
            :obj:`commSignal`: Updated signal (self)
        '''
        
        if self.length == 0:
            self.__sampRate = sig.sampRate

        if not self.__sampRate == sig.sampRate:
            raise TypeError("Signals must have same sampling rate to be extended")
        
        self.updateSignal(np.concatenate([self.signal, sig.signal]))
        return self

    def updateSignal(self, sig):

        ''' Updates the signal

        Args:
            sig (:obj:`numpy array`): New signal array

        Returns:
            :obj:`commSignal`: Updated signal (self)
        '''

        self.__sig = np.array(sig)
        if not self.__sig.size <= self.__sig.shape[0]:
            raise TypeError("The signal array must be 1-D")
        self.__len = len(self.signal)
        return self