'''
Object for different outputs e.g. image, audio.wav etc.
'''
from scipy.io.wavfile import write
import PIL

'''
This object is used to write wav files
'''
class wavFile:

    '''
    This object is used to write wav files
    '''

    def __init__(self, filename, sig):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the wav file
            sig (:obj:`commSignal`): signal to be written
        '''

        self.__fname = filename
        self.__sig = sig


    @property
    def write(self):

        ''' sig (:obj:`wavFile`): writes the signal to file'''

        write(self.__fname, self.__sig.sampRate, self.__sig.signal)
        return self

'''
This object is used to display and write images
'''
class image:

    '''
    This object is used to display and write images
    '''

    def __init__(self, filename, mat):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the wav file
            mat (:obj:`list`): a matrix of pixel values
        '''

        self.__fname = filename
        self.__mat = mat
        self.__image = PIL.Image.fromarray(self.__mat)

    @property
    def write(self):

        ''' sig (:obj:`image`): writes the image to file'''

        self.__image.save(self.__fname)
        return self

    @property
    def show(self):

        ''' sig (:obj:`image`): shows the image'''

        self.__image.show()
        return self