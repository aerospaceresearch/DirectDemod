'''
noaa specific
'''
from directdemod import source, chunker, comm, constants, filters, fmDemod, sink, amDemod
import numpy as np
import logging
import scipy.signal as signal

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
        self.__syncA = None
        self.__syncB = None
        self.__asyncA = None
        self.__asyncB = None

    @property
    def getAudio(self):

        '''Get the audio from data

        Returns:
            :obj:`commSignal`: An audio signal
        '''

        if self.__extractedAudio is None:
            self.__extractedAudio = self.__audio()

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

    def __audio(self, audioFreq = constants.NOAA_AUDSAMPRATE, strictness = True):

        '''Get the audio from data at this sampling rate

        Args:
            audioFreq (:obj:`int`, optional): Target frequency of sampling of audio
            strictness (:obj:`bool`, optional): Strictness of sampling

        Returns:
            :obj:`commSignal`: An audio signal
        '''

        logging.info('Beginning FM demodulation to get audio in chunks')

        audioOut = comm.commSignal(audioFreq)
        bhFilter = filters.blackmanHarris(151)
        fmDemdulator = fmDemod.fmDemod()
        chunkerObj = chunker.chunker(self.__sigsrc)

        for i in chunkerObj.getChunks:

            logging.info('Processing chunk %d of %d chunks', chunkerObj.getChunks.index(i)+1, len(chunkerObj.getChunks))

            sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(*i), chunkerObj).offsetFreq(self.__offset).filter(bhFilter).bwLim(constants.IQ_FMBW, uniq = "First").funcApply(fmDemdulator.demod).bwLim(audioFreq, strictness)
            audioOut.extend(sig)

        logging.info('FM demodulation successfully complete')

        return audioOut

    def __getAM(self, sig):

        '''Do AM demodulation in chunks of given signal

        Args:
            sig (:obj:`comm object`): Input signal

        Returns:
            :obj:`commSignal`: AM demodulated signal
        '''

        logging.info('Beginning AM demodulation in chunks')

        amDemdulator = amDemod.amDemod()
        amOut = comm.commSignal(sig.sampRate)

        chunkerObj = chunker.chunker(sig, chunkSize = 60000*18)

        for i in chunkerObj.getChunks:

            logging.info('Processing chunk %d of %d chunks', chunkerObj.getChunks.index(i)+1, len(chunkerObj.getChunks))
            demodSig = amDemdulator.demod(sig.signal[i[0]:i[1]])
            amOut.extend(comm.commSignal(sig.sampRate, demodSig))

        logging.info('AM demodulation completed')

        return amOut


    def __correlateAndFindPeaks(self, sig, sync):

        '''Correlates given signal and sync signal to find location of syncs

        Args:
            sig (:obj:`comm object`): Input signal
            sync (:obj:`list`): Sync bits

        Returns:
            :obj:`list`: List of detected syncs
        '''

        # create the sync signals, at required sampling frequency
        sampRateCorrection = round(sig.sampRate * constants.NOAA_T)
        sync = np.repeat(sync, sampRateCorrection) - 0.5

        # uncomment below if exact sampling frequency is desired
        #sync = signal.resample(sync, int(sig.sampRate * len(sync)/(sampRateCorrection*1.0/constants.NOAA_T)))

        # correlate signal with syncs
        cor = signal.correlate(sig.signal, sync, mode = 'same')

        # now to find peaks
        # in a second long signal we will expect two peaks, similarly here
        expectedPeaks = int(2*(len(cor) / sig.sampRate)) + 2

        # find indices top expectedPeak number of values
        maxk = np.argpartition(cor, -1*expectedPeaks)[-1*expectedPeaks:]

        # get average height of peaks
        avgpk = np.sum(cor[maxk]) / expectedPeaks 

        # set minimum peak height, 25% less than average
        avgpk -= constants.NOAA_PEAKHEIGHTWIGGLE*(avgpk - (np.sum(cor[np.argpartition(cor, expectedPeaks)[:expectedPeaks]]) / expectedPeaks))

        # get all signal locations where it is above this
        possiblePeaks = np.sort(np.argwhere(cor > avgpk).ravel())

        # minimum distance between peaks is about 0.45 seconds i.e. 50 ms wiggle room
        minPkDist = constants.NOAA_MINPEAKDIST * sig.sampRate

        absolutePeaks = []
        currentMax = None
        currentMaxIndex = None

        # go through the list of possible peaks abd pick the maximum one in each group
        for i in np.nditer(possiblePeaks):
            if not currentMaxIndex is None and (i - currentMaxIndex) >= minPkDist:
                absolutePeaks.append(currentMaxIndex)
                currentMax = None
                currentMaxIndex = None

            if currentMax is None or currentMax < cor[i]:
                currentMax = cor[i]
                currentMaxIndex = i

        absolutePeaks.append(currentMaxIndex)

        absolutePeaks = np.sort(np.array(absolutePeaks).ravel())

        return absolutePeaks
        

    @property
    def getCrudeSync(self):

        '''Get the sync locations: at constants.NOAA_CRUDESYNCSAMPRATE sampling rate

        Returns:
            :obj:`list`: A list of locations of sync in sample number
        '''

        if self.__syncA is None or self.__syncB is None:
            sig = self.__audio(constants.NOAA_CRUDESYNCSAMPRATE, False) 

            # first get the AM demodulated signal at required sampling rate
            sig = self.__getAM(sig)

            self.__syncCrudeSampRate = sig.sampRate

            logging.info('Beginning SyncA detection')
            self.__syncA = self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCA)
            logging.info('Done SyncA detection')

            logging.info('Beginning SyncB detection')
            self.__syncB = self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCB)
            logging.info('Done SyncB detection')

        return [self.__syncA, self.__syncB]

    @property
    def getAccurateSync(self):

        '''Get the sync locations: at highest sampling rate

        Returns:
            :obj:`list`: A list of locations of sync in sample number
        '''

        if self.__asyncA is None or self.__asyncB is None:
            if self.__syncA is None or self.__syncB is None:
                self.getCrudeSync

            # calculate the width of search window in sample numbers
            syncTime = constants.NOAA_T * len(constants.NOAA_SYNCA)
            searchTimeWidth = 3 * syncTime
            searchSampleWidth = int(searchTimeWidth * self.__sigsrc.sampFreq)

            # convert sync from samples to time
            csyncA = self.__syncA / self.__syncCrudeSampRate
            csyncB = self.__syncB / self.__syncCrudeSampRate

            # convert back to sample number
            csyncA *= self.__sigsrc.sampFreq
            csyncB *= self.__sigsrc.sampFreq

            ## Accurate syncA
            self.__asyncA = []
            logging.info('Beginning Accurate SyncA detection')

            for i in csyncA:
                startI = int(i) - int(searchSampleWidth)
                endI = int(i) + int(searchSampleWidth)
                if startI < 0 or endI > self.__sigsrc.length:
                    continue
                sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(startI, endI)).offsetFreq(self.__offset).filter(filters.blackmanHarris(151, zeroPhase = True)).funcApply(fmDemod.fmDemod().demod).funcApply(amDemod.amDemod().demod)
                self.__asyncA.append(self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCA)[0] + startI)

            logging.info('Accurate SyncA detection complete')

            ## Accurate syncB
            self.__asyncB = []
            logging.info('Beginning Accurate SyncB detection')

            for i in csyncB:
                startI = int(i) - int(searchSampleWidth)
                endI = int(i) + int(searchSampleWidth)
                if startI < 0 or endI > self.__sigsrc.length:
                    continue
                sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(startI, endI)).offsetFreq(self.__offset).filter(filters.blackmanHarris(151, zeroPhase = True)).funcApply(fmDemod.fmDemod().demod).funcApply(amDemod.amDemod().demod)
                self.__asyncB.append(self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCB)[0] + startI)

            logging.info('Accurate SyncB detection complete')


        return [self.__asyncA, self.__asyncB]


