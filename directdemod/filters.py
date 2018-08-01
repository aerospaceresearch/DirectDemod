'''
Object for filters
'''

import directdemod.constants as constants
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

            retDat, self.__zi = signal.lfilter(self.__b, self.__a, x, zi = self.__zi)
            return retDat
        else:
            if self.__zeroPhase:
                return signal.filtfilt(self.__b, self.__a, x)
            else:
                return signal.lfilter(self.__b, self.__a, x)

    @property
    def getA(self):

        ''':obj:`list`: Get 'a' of the filter'''

        return self.__a

    @property
    def getB(self):
        
        ''':obj:`list`: Get 'b' of the filter'''

        return self.__b

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
Blackman Harris filter
'''

class blackmanHarris(filter):

    '''
    Blackman Harris filter
    '''

    def __init__(self, n, storeState = True, zeroPhase = False, initOut = None):

        '''Initialize the object

        Args:
            n (:obj:`int`): size of the window
            storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
            zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
            initOut (:obj:`list`, optional): Initial condition of the filter

        '''

        self.__n = n
        super(blackmanHarris, self).__init__(signal.blackmanharris(self.__n), [1], storeState, zeroPhase, initOut)

'''
Blackman Harris filter (by convolving)
'''

class blackmanHarrisConv:

    '''
    Blackman Harris filter (by convolving, Not recommended for large signals)
    '''

    def __init__(self, n = 151):

        '''Initialize the object

        Args:
            n (:obj:`int`, optional): size of the window

        '''

        self.__n = n
        self.__window = signal.blackmanharris(self.__n)

    def applyOn(self, sig):

        '''Apply the filter to a given array of signal

        Args:
            x (:obj:`numpy array`): The signal array on which the filter needs to be applied

        Returns:
            :obj:`numpy array`: Filtered signal array
        '''

        return signal.convolve(sig, self.__window, mode='same')

'''
Hamming filter
'''

class hamming(filter):

    '''
    Hamming filter
    '''

    def __init__(self, n, storeState = True, zeroPhase = False, initOut = None):

        '''Initialize the object

        Args:
            n (:obj:`int`): size of the window
            storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
            zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
            initOut (:obj:`list`, optional): Initial condition of the filter

        '''

        self.__n = n
        super(hamming, self).__init__(signal.hamming(self.__n), [1], storeState, zeroPhase, initOut)

'''
Gaussian filter
'''

class gaussian(filter):

    '''
    Gaussian filter
    '''

    def __init__(self, n, sigma, storeState = True, zeroPhase = False, initOut = None):

        '''Initialize the object

        Args:
            n (:obj:`int`): size of the window
            sigma (:obj:`float`): The standard deviation
            storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
            zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
            initOut (:obj:`list`, optional): Initial condition of the filter

        '''

        self.__n = n
        self.__sigma = sigma
        super(gaussian, self).__init__(signal.gaussian(self.__n, self.__sigma), [1], storeState, zeroPhase, initOut)

'''
Butterworth filter
'''

class butter(filter):

    '''
    Butterworth filter
    '''

    def __init__(self, Fs, cutoffA, cutoffB = None, n = 6, typeFlt = constants.FLT_LP, storeState = True, zeroPhase = False, initOut = None):

        '''Initialize the object

        Args:
            Fs (:obj:`int`): Sampling frequency of signal
            cutoffA (:obj:`float`): desired cutoff A of filter in Hz
            cutoffB (:obj:`float`, optional): desired cutoff B of filter in Hz
            n (:obj:`int`, optional): Order of filter
            type (:obj:`constant`, optional): constants.FLT_LP to constants.FLT_BS, see constants module
            storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
            zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
            initOut (:obj:`list`, optional): Initial condition of the filter

        '''
        self.__Fs = Fs
        self.__cutoffA = cutoffA
        self.__cutoffB = cutoffB
        self.__n = n
        self.__type = typeFlt

        if (self.__type == constants.FLT_BP or self.__type == constants.FLT_BS) and self.__cutoffB is None:
            raise ValueError("CutoffB must be given")

        if self.__type == constants.FLT_LP:
            self.__b, self.__a = signal.butter(self.__n, self.__cutoffA / (0.5 * self.__Fs), btype='lowpass')
        elif self.__type == constants.FLT_HP:
            self.__b, self.__a = signal.butter(self.__n, self.__cutoffA / (0.5 * self.__Fs), btype='highpass')
        elif self.__type == constants.FLT_BP:
            self.__b, self.__a = signal.butter(self.__n, [self.__cutoffA / (0.5 * self.__Fs), self.__cutoffB / (0.5 * self.__Fs)] , btype='bandpass')
        elif self.__type == constants.FLT_BS:
            self.__b, self.__a = signal.butter(self.__n, [self.__cutoffA / (0.5 * self.__Fs), self.__cutoffB / (0.5 * self.__Fs)] , btype='bandstop')
        else:
            raise ValueError("Invalid filter type")

        super(butter, self).__init__(self.__b, self.__a, storeState, zeroPhase, initOut)

'''
Remez band filter
'''

class remez(filter):

    '''
    Remez band filter
    '''

    def __init__(self, Fs, bands, gains, ntaps = 128, storeState = True, zeroPhase = False, initOut = None):

        '''Initialize the object

        Args:
            Fs (:obj:`int`): sampling frequency in Hz
            bands (:obj:`list`): non-overlapping list of bands (in Hz) in increasing order. e.g [[0, 100], [400, 500], [600, 700]]
            gains (:obj:`float`): Corresponding gains of the bands e.g. [0, 1, 0.5]
            ntaps (:obj:`int`, optional): Number of taps of filter (number of terms in filter)
            storeState (:obj:`bool`, optional): Whether the filter state must be stored. Useful when filtering a chunked signal to avoid border effects.
            zeroPhase (:obj:`bool`, optional): Whether the filter has to provide zero phase error to the input i.e. no delay in the output (Note: Enabling this will disable 'storeState' and 'initOut')
            initOut (:obj:`list`, optional): Initial condition of the filter

        '''

        if len(bands) == 0:
            raise ValueError("Atleast one band must be given")

        if bands[-1][1] >= (Fs/2):
            raise ValueError("Last band must end before (Fs/2)Hz")

        self.__bands = []
        for i in bands:
            self.__bands.extend(i)
        self.__gains = gains

        if not len(self.__bands) == 2*len(self.__gains):
            raise ValueError("Invalid bands/gains values")

        super(remez, self).__init__(signal.remez(ntaps, self.__bands, self.__gains, Hz = Fs), [1], storeState, zeroPhase, initOut)


'''
To be implemented later if needed
'''


class medianFilter:
    def __init__(self, n = 5):
        self.__n = n
    def applyOn(self, sig):
        return signal.medfilt(sig, self.__n)
