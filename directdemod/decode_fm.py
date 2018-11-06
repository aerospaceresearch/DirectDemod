'''
fm specific
'''
from directdemod import source, sink, chunker, comm, constants, filters, demod_am, demod_fm
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavf
import time


'''
Object to decode wide or narrow FM
'''

class decode_fm:

    '''
    Object to decode wide or narrow FM
    '''

    def __init__(self, sigsrc, offset, bw = None, audioFreq = None):

        '''Initialize the object

        Args:
            sigsrc (:obj:`commSignal`): IQ data source
            offset (:obj:`float`): Frequency offset of source in Hz
            bw (:obj:`int`, optional): Bandwidth
        '''
        self.__bw = bw
        if self.__bw is None:
            self.__bw = 30000
        self.__sigsrc = sigsrc
        self.__offset = offset
        self.__audioFreq = audioFreq
        if self.__audioFreq is None:
            self.__audioFreq = 15000
        self.__strictness = True


    @property
    def getAudio(self):

        '''Get the audio from data

        Returns:
            :obj:`commSignal`: An audio signal
        '''

        audioFreq = self.__audioFreq
        strictness = self.__strictness
        #print(audioFreq, self.__bw)

        audioOut = comm.commSignal(audioFreq)
        bhFilter = filters.blackmanHarris(151)
        fmDemdulator = demod_fm.demod_fm()
        chunkerObj = chunker.chunker(sigsrc)
        #print(chunkerObj.getChunks)
        #print(len(chunkerObj.getChunks[:10]))

        for i in chunkerObj.getChunks:
            offset = self.__offset

            sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(*i), chunkerObj)\
                .offsetFreq(self.__offset).filter(bhFilter)\
                .bwLim(self.__bw, uniq="First")\
                .funcApply(fmDemdulator.demod)\
                .bwLim(audioFreq, strictness)

            audioOut.extend(sig)

        return audioOut


if __name__ == "__main__":

    time_start = time.time()

    fileName = "C:/Users/station/Desktop/ariss_funkfreunde/" \
               "2018-10-23T09-13-13.502916Z_2018-10-23T09-27-13.502916Z_1556987c-f74f-471e-90c1-514f4fbb4bc0_a74386a0-feac-4aa4-a9a8-d67ae05614a7.dat"

    samplerate = 2048000
    givenSampRate = samplerate

    # create this as a signal source
    sigsrc = None
    if fileName[-3:] == "wav":
        sigsrc = source.IQwav(fileName, givenSampRate)
    elif fileName[-3:] == "dat":
        sigsrc = source.IQdat(fileName, givenSampRate)

    audioFreq = 15000
    bw = 30000
    offset = 0.0

    audioOut = decode_fm(sigsrc, offset=offset, bw=bw, audioFreq=audioFreq)
    audioOut_signal = audioOut.getAudio.signal

    #plt.plot(audioOut_signal)
    #plt.savefig("wave2.png")
    #plt.show()
    #plt.clf()

    fs = audioFreq
    out_f = 'out2.wav'
    wavf.write(out_f, fs, audioOut_signal)
    print("it took me", time.time()-time_start, "seconds")