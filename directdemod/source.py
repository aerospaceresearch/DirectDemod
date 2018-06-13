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
    An IQ.wav file source, typically an output recorded from SDRSHARP or other similar software
    '''
    def __init__(self, filename, givenSampFreq = None):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the IQ.wav file
        '''

        self.__offset = 0
        self.__sourceType = constants.SOURCE_IQWAV
        self.__sampFreq, self.__data = scipy.io.wavfile.read(filename, True)
        if not givenSampFreq is None:
            self.__sampFreq = givenSampFreq
        self.__actualLength = self.__data.shape[0]
        self.__length = self.__data.shape[0]

    @property
    def sampFreq(self):

        ''':obj:`int`: get sampling freq of source'''

        return self.__sampFreq

    @property
    def sourceType(self):

        ''':obj:`int`: get source type'''

        return self.__sourceType

    @property
    def length(self):

        ''':obj:`int`: get source length'''

        return self.__length

    def read(self, fromIndex, toIndex = None):

        '''Read source data

        Args:
            fromIndex (:obj:`int`): starting index
            toIndex (:obj:`int`, optional): ending index. If not provided, the element at location given by fromIndex is returned

        Returns:
            :obj:`numpy array`: Complex IQ numbers in an array
        '''

        fromIndex += self.__offset

        if toIndex == None:
            toIndex = fromIndex + 1
        else:
            toIndex += self.__offset

        if fromIndex-self.__offset < 0 or toIndex-self.__offset < 0 or fromIndex-self.__offset >= self.length or toIndex-self.__offset > self.length:
            raise ValueError("fromIndex and toIndex have invalid values")

        samples = self.__data[fromIndex:toIndex,0] + 1j * self.__data[fromIndex:toIndex,1]
        return np.array(samples).astype("complex64") - (127.5 + 1j*127.5)

    def limitData(self, initOffset = None, finalLimit = None):

        '''Limit source data

        Args:
            initOffset (:obj:`int`, optional): starting index
            finalLimit (:obj:`int`, optional): ending index

        '''

        if not initOffset is None:
            self.__offset = initOffset
        else:
            self.__offset = 0

        if not finalLimit is None:
            self.__length = finalLimit -  self.__offset
        else:
            self.__length = self.__actualLength

'''
An IQ.dat file source
The IQ dat file contains two channels, one channel for I component and the other for Q
'''
class IQdat(source):
    '''
    An IQ.dat file source
    '''
    def __init__(self, filename, givenSampFreq = None):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the IQ.dat file
        '''

        self.__offset = 0
        self.__sourceType = constants.SOURCE_IQDAT
        self.__data = np.memmap(filename)
        self.__length = int(len(self.__data)/2)
        self.__sampFreq = constants.IQ_SDRSAMPRATE
        if not givenSampFreq is None:
            self.__sampFreq = givenSampFreq
        self.__actualLength = int(len(self.__data)/2)

    @property
    def sampFreq(self):

        ''':obj:`int`: get sampling freq of source'''

        return self.__sampFreq

    @property
    def sourceType(self):

        ''':obj:`int`: get source type'''

        return self.__sourceType

    @property
    def length(self):

        ''':obj:`int`: get source length'''

        return self.__length

    def read(self, fromIndex, toIndex = None):

        '''Read source data

        Args:
            fromIndex (:obj:`int`): starting index
            toIndex (:obj:`int`, optional): ending index. If not provided, the element at location given by fromIndex is returned

        Returns:
            :obj:`numpy array`: Complex IQ numbers in an array
        '''

        fromIndex += self.__offset

        if toIndex == None:
            toIndex = fromIndex + 1
        else:
            toIndex += self.__offset

        if fromIndex-self.__offset < 0 or toIndex-self.__offset < 0 or fromIndex-self.__offset >= self.length or toIndex-self.__offset > self.length:
            raise ValueError("fromIndex and toIndex have invalid values")
            
        samples = (self.__data[2*fromIndex:2*toIndex:2]) + 1j * (self.__data[1+2*fromIndex:1+2*toIndex:2])
        return np.array(samples).astype("complex64") - (127.5 + 1j*127.5)

    def limitData(self, initOffset = None, finalLimit = None):

        '''Limit source data

        Args:
            initOffset (:obj:`int`, optional): starting index
            finalLimit (:obj:`int`, optional): ending index

        '''

        if not initOffset is None:
            self.__offset = initOffset
        else:
            self.__offset = 0

        if not finalLimit is None:
            self.__length = finalLimit -  self.__offset
        else:
            self.__length = self.__actualLength

'''
Note: This is an alternative implementation, directly using np.memmap
An IQ.wav file source, typically an output recorded from SDRSHARP
The IQ wav file contains two channels, one channel for I component and the other for Q
'''
class IQwavAlt(source):
    '''
    Note: This is an alternative implementation, directly using np.memmap
    An IQ.wav file source, typically an output recorded from SDRSHARP
    '''
    def __init__(self, filename, givenSampFreq = None):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the IQ.wav file
        '''

        self.__offset = 0
        self.__sourceType = constants.SOURCE_IQWAV
        self.__data = np.memmap(filename, offset=44)
        self.__length = int(len(self.__data)/2)
        self.__sampFreq = constants.IQ_SDRSAMPRATE
        if not givenSampFreq is None:
            self.__sampFreq = givenSampFreq
        self.__actualLength = int(len(self.__data)/2)

    @property
    def sampFreq(self):

        ''':obj:`int`: get sampling freq of source'''

        return self.__sampFreq

    @property
    def sourceType(self):

        ''':obj:`int`: get source type'''

        return self.__sourceType

    @property
    def length(self):

        ''':obj:`int`: get source length'''

        return self.__length

    def read(self, fromIndex, toIndex = None):

        '''Read source data

        Args:
            fromIndex (:obj:`int`): starting index
            toIndex (:obj:`int`, optional): ending index. If not provided, the element at location given by fromIndex is returned

        Returns:
            :obj:`numpy array`: Complex IQ numbers in an array
        '''

        fromIndex += self.__offset

        if toIndex == None:
            toIndex = fromIndex + 1
        else:
            toIndex += self.__offset

        if fromIndex-self.__offset < 0 or toIndex-self.__offset < 0 or fromIndex-self.__offset >= self.length or toIndex-self.__offset > self.length:
            raise ValueError("fromIndex and toIndex have invalid values")
            
        samples = (self.__data[2*fromIndex:2*toIndex:2]) + 1j * (self.__data[1+2*fromIndex:1+2*toIndex:2])
        return np.array(samples).astype("complex64") - (127.5 + 1j*127.5)

    def limitData(self, initOffset = None, finalLimit = None):

        '''Limit source data

        Args:
            initOffset (:obj:`int`, optional): starting index
            finalLimit (:obj:`int`, optional): ending index

        '''

        if not initOffset is None:
            self.__offset = initOffset
        else:
            self.__offset = 0

        if not finalLimit is None:
            self.__length = finalLimit -  self.__offset
        else:
            self.__length = self.__actualLength