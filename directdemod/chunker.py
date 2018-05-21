'''
chunking helper
'''
import directdemod.constants as constants
import math

'''
This object is just to help in chunking process
It is responsible for creating chunks of the signal and store the info to be used later
It can be helpful for avoiding border issues in filters and demods
'''

# POSSIBLE TODO: automatic distinction in get/set for every cycle. will avoid need of 'uniq'

class chunker:

    '''
    This object is just to help in chunking process
    '''

    def __init__(self, sigsrc, chunkSize = constants.PROC_CHUNKSIZE):

        '''Initialize the object

        Args:
            sampRate (:obj:`commSignal`): commSignal object to be chunked
            chunkSize (:obj:`int`, optional): chunk size
        '''

        self.__nChunks = math.ceil(sigsrc.length*1.0/chunkSize)
        self.__chunks = []
        self.__vars = {}
        i = 0

        # create normal sized chunks
        while(i + chunkSize < sigsrc.length):
            self.__chunks.append([i,i + chunkSize])
            i += chunkSize 

        # has it exhaused the whole signal?
        if len(self.__chunks) == 0:
            self.__chunks.append([0,sigsrc.length])
        else: # if not put the remaining as another smaller chunk
            if not self.__chunks[-1][1] == sigsrc.length:
                self.__chunks.append([self.__chunks[-1][1],sigsrc.length])

    @property
    def getChunks(self):

        ''':obj:`list`: get the created chunks'''

        return self.__chunks

    def set(self, name, value):

        '''set a variable for to be used during chunking

        Args:
            name (:obj:`str`): name of the variable
            value (:obj:`anything`, optional): value of variable
        '''

        self.__vars[name] = value

    def get(self, name, init = None):

        '''get a variable value for to be used during chunking

        Args:
            name (:obj:`str`): name of the variable
            init (:obj:`anything`): initialize variable to this, if undefined previously

        Returns:
            :obj:`aything`: value of variable
        '''

        if init is None:
            return self.__vars[name]
        else:
            try:
                return self.__vars[name]
            except:
                self.__vars[name] = init
                return self.__vars[name]