'''
noaa specific
'''
from directdemod import source, chunker, comm, constants, filters, fmDemod, sink, amDemod
import numpy as np
import logging

'''
Object to decode NOAA APT
'''

class noaa:

    '''
    Object to decode NOAA APT
    '''

    def __init__(self, sigsrc, offset):

        '''Initialize the object

        Args:
            sigsrc (:obj:`commSignal`): IQ data source
            offset (:obj:`float`): Frequency offset of source in Hz
        '''

        self.__sigsrc = sigsrc
        self.__offset = offset
        self.__extractedAudio = None
        self.__image = None

    @property
    def getAudio(self):

        '''Get the audio from data

        Returns:
            :obj:`commSignal`: An audio signal
        '''

        if self.__extractedAudio is None:

            logging.info('Beginning FM demodulation to get audio in chunks')

            audioOut = comm.commSignal(constants.NOAA_AUDSAMPRATE)
            bhFilter = filters.blackmanHarris(151)
            fmDemdulator = fmDemod.fmDemod()
            chunkerObj = chunker.chunker(self.__sigsrc)

            for i in chunkerObj.getChunks:

                logging.info('Processing chunk %d of %d chunks', chunkerObj.getChunks.index(i)+1, len(chunkerObj.getChunks))

                sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(*i), chunkerObj).offsetFreq(self.__offset).filter(bhFilter).bwLim(constants.IQ_FMBW, uniq = "First").funcApply(fmDemdulator.demod).bwLim(constants.NOAA_AUDSAMPRATE, True)
                audioOut.extend(sig)

            self.__extractedAudio = audioOut

            logging.info('FM demodulation successfully complete')

        return self.__extractedAudio

    @property
    def getImage(self):

        '''Get the image from data

        Returns:
            :obj:`numpy array`: A matrix of pixel values
        '''

        if self.__image is None:
            if self.__extractedAudio is None:
                self.getAudio()

            logging.info('Beginning AM demodulation to get image')

            self.__extractedAudio.updateSignal(self.__extractedAudio.signal[:constants.NOAA_AUDSAMPRATE*int(self.__extractedAudio.length // constants.NOAA_AUDSAMPRATE)]).funcApply(amDemod.amDemod().demod).filter(filters.medianFilter())
            reshaped = self.__extractedAudio.signal.reshape(self.__extractedAudio.length // 5, 5)
            (low, high) = np.percentile(reshaped[:, 2], (0.5, 99.5))
            delta = high - low
            data = np.round(255 * (reshaped[:, 2] - low) / delta)
            data[data < 0] = 0
            data[data > 255] = 255
            digitized = data.astype(np.uint8)
            self.__image = digitized.reshape((int(len(digitized) / 2080), 2080))

            logging.info('AM demodulation successfully complete')

        return self.__image

