'''
Funcube
'''
from directdemod import source, sink, chunker, comm, constants, filters
import numpy as np
import logging
import scipy.signal as signal
#import matplotlib.pylab as plt
import math, time

## Inspired from: https://github.com/dbdexter-dev/meteor_demod
# Thank you!

################# OBJECTS

class agc():
    def __init__(self):
        self.mean = 180.0
        self.dc = 0.0

    def adjust(self, inp):

        # moving avg to get dc
        self.dc = ((self.dc * ((1024*1024)-1)*1.0) + inp) / (1024*1024*1.0)
        inp -= self.dc

        # moving avg of amplitude
        self.mean = (self.mean * 1.0 * (65536.0 - 1) + ((np.real(inp)*np.real(inp) + np.imag(inp)*np.imag(inp))**0.5)) / 65536.0

        # multiply the input value
        if 180.0 / self.mean > 20:
            return inp * 20
        else:
            return inp * 180.0 / self.mean

class costas():

    def __init__(self):
        self.freq = 0.001
        self.phase = 0.00
        self.output = np.exp(-1j*self.phase)

        self.damping = 0.70710678118
        self.bw = 0.05235833333
        self.compAlphaBeta(self.damping, self.bw)

        self.mean = 1.0
        self.plllock = False

        self.hypstore = []
        for i in range(256):
            self.hypstore.append(np.tanh(i-128))

    def compAlphaBeta(self, damping, bw):
        denom = (1.0 + 2.0*damping*bw + bw*bw)
        self.alpha = (4*damping*bw)/denom
        self.beta = (4*bw*bw)/denom

    def loop(self, samp):
        self.output = np.exp(-1j*self.phase)

        correctedIn = samp * self.output

        error = np.imag(correctedIn) * self.hyp(np.real(correctedIn))/255.0
        self.mean = (self.mean * (39999.0) + np.abs(error))/40000.0
        if error > 1: 
            error = 1.0
        elif (error < -1):
            error = -1.0

        self.phase = math.fmod(self.phase + self.freq + self.alpha*error, 2*np.pi)
        self.freq = self.freq + self.beta*error

        if not self.plllock and self.mean < 0.2:
            self.compAlphaBeta(self.damping, self.bw/2.0)
            self.plllock = True
        elif self.plllock and self.mean > 0.5:
            self.compAlphaBeta(self.damping, self.bw)
            self.plllock = False
        return correctedIn

    def hyp(self, x):
        if x > 127: return 1
        if x < -128: return -1
        return self.hypstore[int(x+128)]

def lim(x):
    if x < -128.0:
        return -128
    if x > 127.0:
        return 127
    if x > 0 and x < 1:
        return 1
    if x > -1 and x < 0:
        return -1
    return int(x)

def limBin(x):
    if x <= 0:
        return 0
    else:
        return 1


'''
Object to Funcube
'''

class decode_funcube:

    '''
    Object to decode Funcube
    '''

    def __init__(self, sigsrc, offset, bw):

        '''Initialize the object

        Args:
            sigsrc (:obj:`commSignal`): IQ data source
            offset (:obj:`float`): Frequency offset of source in Hz
            bw (:obj:`int`, optional): Bandwidth
        '''

        self.__bw = bw
        if self.__bw is None:
            self.__bw = 7000
        self.__sigsrc = sigsrc
        self.__offset = offset
        self.__useful = 0

    @property
    def useful(self):

        '''See if signal was found

        Returns:
            :obj:`int`: 0 if not found, 1 if found
        '''

        return self.__useful

    @property
    def getSyncs(self):

        '''Get syncs of Funcube

        Returns:
            :obj:`list`: list of detected syncs
        '''

        # create chunker object
        chunkerObj = chunker.chunker(self.__sigsrc)

        # butter filter
        bf = filters.butter(self.__sigsrc.sampFreq, self.__bw)

        # init vars for gardner
        symbolPeriod = self.__sigsrc.sampFreq/12000
        timing = 0.00
        gardnerC, gardnerB, gardnerA = 0.00, 0.00, 0.00
        agcObj = agc()
        pllObj = costas()
        ctr = 0

        sync = np.array([int(i) for i in "101000110001000000000001010111100"])

        sync12khz = np.repeat(sync, 10)

        sync[sync == 1] = 127
        sync[sync == 0] = -128
        sync2mhz = np.repeat(sync, int(2048000/1200))

        maxResBuff = []
        minResBuff = []
        maxBuffRetain = -1
        maxBuffStart = 0

        minSyncs = []
        maxSyncs = []

        numCtrs = int(chunkerObj.getChunks[-1][-1]*12000/2048000)
        start_time = time.time()
        lastMin = None
        ctrMain = 0
        for i in chunkerObj.getChunks[:]:

            #interpolate
            sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(*i))
            sig.offsetFreq(self.__offset)
            sig.filter(bf)

            # main loop
            for i in sig.signal:

                ### MAXSYNC detection by correlation

                # start storing 2mhz values near sync possible regions
                if not lastMin is None and (ctr > lastMin + (4.9*12000) - (2*len(sync12khz)) or not maxBuffRetain == -1):
                    if len(maxResBuff) == 0:
                        maxBuffStart = ctrMain
                    maxResBuff.append(lim(np.real(i*pllObj.output)/2))

                # see if correlation is to be performed
                if maxBuffRetain == -1:
                    if len(maxResBuff) > (2 * len(sync2mhz)):
                        maxBuffStart += 1
                        maxResBuff.pop(0)
                elif maxBuffRetain == 0:
                    maxBuffRetain -= 1
                    corr = np.abs(np.correlate(maxResBuff,sync2mhz, mode='same'))
                    logging.info("MAXSYNC %d", maxBuffStart+np.argmax(corr))
                    #print("MAXSYNC", maxBuffStart, np.argmax(corr), maxBuffStart+np.argmax(corr))
                    maxSyncs.append(maxBuffStart+np.argmax(corr))
                    maxResBuff = []

                    #plt.plot(corr)
                    #plt.show()
                else:
                    maxBuffRetain -= 1

                # Gardners algorithm
                if timing >= symbolPeriod/2 and timing < ((symbolPeriod/2)+1):
                    gardnerB = agcObj.adjust(i)

                elif timing >= symbolPeriod:
                    gardnerA = agcObj.adjust(i)
                    timing -= symbolPeriod
                    resync_error = (np.imag(gardnerA) - np.imag(gardnerC)) * np.imag(gardnerB)
                    timing += (resync_error*symbolPeriod/(2000000.0))
                    gardnerC = gardnerA
                    gardnerA = pllObj.loop(gardnerA)
                    ctr += 1

                    # 12khz buffer
                    minResBuff.append(limBin(np.real(gardnerA)))
                    minResBuff = minResBuff[-1*len(sync12khz):]

                    # print periodic status
                    try:
                        if ctr%1000 == 0:
                            logging.info("[%.2f percent complete] [%.2f seconds elapsed] [%.2f seconds remain]", (ctr*100/numCtrs), (time.time() - start_time), (((time.time() - start_time)/(ctr/numCtrs))-(time.time() - start_time)))
                            #print(ctr, '[%.2f' %(ctr*100/numCtrs),"%]",'[%.2f' %(time.time() - start_time),"seconds elapsed]",'[%.2f' %(((time.time() - start_time)/(ctr/numCtrs))-(time.time() - start_time)), "seconds remaining]", pllObj.mean)
                    except:
                        pass

                    # see if sync is present
                    if len(minResBuff) == len(sync12khz) and np.abs(np.sum(np.abs(np.array(minResBuff) - sync12khz)) - (len(sync12khz)/2)) > 120:
                        logging.info("MINSYNC: %d %f",ctr, np.abs(np.sum(np.abs(np.array(minResBuff) - sync12khz)) - (len(sync12khz)/2)))
                        #print("MINSYNC:",ctr, np.abs(np.sum(np.abs(np.array(minResBuff) - sync12khz)) - (len(sync12khz)/2)))
                        minSyncs.append(ctr)
                        lastMin = ctr
                        maxBuffRetain = 2 * len(sync2mhz)

                timing += 1
                ctrMain += 1

        if len(maxSyncs) > 0:
            # check usefulness
            if np.min(np.abs(np.diff(maxSyncs) - (4.98*2048000))) < (0.2*2048000):
                self.__useful = 1
            return list(maxSyncs)[1:]
        else:
            return []
        