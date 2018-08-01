'''
Object for different outputs e.g. image, audio.wav etc.
'''
from scipy.io.wavfile import write
import PIL, itertools

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
            filename (:obj:`str`): filename of the image file
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

'''
This object is used to write to .csv files
'''
class csv:

    '''
    This object is used to write to .csv files
    '''

    def __init__(self, filename, data, titles = None):

        '''Initialize the object

        Args:
            filename (:obj:`str`): filename of the csv file
            data (:obj:`list`): data to be written
            titles (:obj:`list`): titles of columns
        '''

        self.__fname = filename
        self.__data = data
        self.__title = titles

    @property
    def write(self):

        ''' sig (:obj:`csv`): writes the data to file'''

        f = open(self.__fname, 'w')
        if not self.__title is None:
            print("".join([str(i)+"," for i in self.__title]), file=f)
        for i in list(itertools.zip_longest(*self.__data, fillvalue='')):
            print("".join([str(j)+"," for j in i]), file=f)
        return self