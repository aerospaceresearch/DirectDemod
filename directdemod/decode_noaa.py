'''
noaa specific
'''
from directdemod import source, sink, chunker, comm, constants, filters, demod_am, demod_fm
import numpy as np
import logging, colorsys
import scipy.signal as signal
from scipy import stats
import scipy.ndimage
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy import misc
from PIL import Image

'''
Object to decode NOAA APT
'''

class decode_noaa:

    '''
    Object to decode NOAA APT
    '''

    def __init__(self, sigsrc, offset, bw = None):

        '''Initialize the object

        Args:
            sigsrc (:obj:`commSignal`): IQ data source
            offset (:obj:`float`): Frequency offset of source in Hz
            bw (:obj:`int`, optional): Bandwidth
        '''
        self.__bw = bw
        if self.__bw is None:
            self.__bw = constants.NOAA_FMBW
        self.__sigsrc = sigsrc
        self.__offset = offset
        self.__extractedAudio = None
        self.__image = None
        self.__syncA = None
        self.__syncB = None
        self.__asyncA = None
        self.__asyncB = None
        self.__audOut = None
        self.__asyncApk = None
        self.__asyncAtime = None
        self.__asyncBpk = None
        self.__asyncBtime = None
        self.__useNormCorrelate = None
        self.__color = None
        self.__useful = 0
        self.__chIDA = None
        self.__chIDB = None

    @property
    def channelID(self):
        '''get channel ID's

        Returns:
            :obj:`list`: [channelIDA, channelIDB]
        '''

        if self.__image is None:
            self.getImage

        return [self.__chIDA, self.__chIDB]

    @property
    def useful(self):

        '''See if some data was found or not: 10 consecutive syncs apart by 0.5s+-error

        Returns:
            :obj:`int`: 0 if not found, 1 if found
        '''

        if self.__syncA is None or self.__syncB is None:
            self.getCrudeSync()

        return self.__useful

    @property
    def getAudio(self):

        '''Get the audio from data

        Returns:
            :obj:`commSignal`: An audio signal
        '''

        if self.__extractedAudio is None:
            self.__extractedAudio = self.__audio()

        return self.__extractedAudio

    def getMapImage(self, cTime, destFileRot, destFileNoRot, satellite, tleFile = None):

        '''Get the map overlay of the image

        Args:
            cTime (:obj:`datetime`): Time of start of capture in UTC
            tleFile (:obj:`str`, optional): TLE file location, pulls latest from internet if not given
            destFile (:obj:`str`): location where to store the image
            satellite (:obj:`str`): Satellite name, ex: NOAA 19 etc.

        '''

        try:
            from pyorbital.orbital import Orbital
            from pyorbital import tlefile
        except ImportError:
            logging.error('pyorbital not installed')
            return
            
        basemapPresent = False
        cartopyPresent = False

        try:
            from mpl_toolkits.basemap import Basemap
            basemapPresent = True
        except ImportError:
            logging.warning('basemap not installed')

        if not basemapPresent:
            try:
                import cartopy.crs as ccrs
                import cartopy.feature
                cartopyPresent = True
            except ImportError:
                logging.error('Both basemap and cartopy not installed. Please install either.')
                return

        def angleFromCoordinate(lat1, long1, lat2, long2):
            # source: https://stackoverflow.com/questions/3932502/calculate-angle-between-two-latitude-longitude-points
            lat1 = np.radians(lat1)
            long1 = np.radians(long1)
            lat2 = np.radians(lat2)
            long2 = np.radians(long2)

            dLon = (long2 - long1)

            y = np.sin(dLon) * np.cos(lat2)
            x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dLon)
            brng = np.arctan2(y, x)
            brng = np.degrees(brng)
            brng = (brng + 360) % 360
            brng = 360 - brng
            return brng

        if tleFile is None:
            orb = Orbital(satellite)
        else:
            orb = Orbital(satellite, tle_file=tleFile)

        im = self.getImageA
        im = im[:,85:995]
        oim = im[:]

        tdelta = int(im.shape[0]/16)
        if tdelta < 10:
            tdelta = 10

        top = orb.get_lonlatalt(cTime + timedelta(seconds=int(im.shape[0]/4) - tdelta))[:2][::-1]
        bot = orb.get_lonlatalt(cTime + timedelta(seconds=int(im.shape[0]/4) + tdelta))[:2][::-1]
        center = orb.get_lonlatalt(cTime + timedelta(seconds=int(im.shape[0]/4)))[:2][::-1]

        rot = angleFromCoordinate(*bot, *top)

        if basemapPresent:
            rotated_img = ndimage.rotate(im, rot)
            rimg = rotated_img[:]
            w = rotated_img.shape[1]
            h = rotated_img.shape[0]

            m = Basemap(projection='cass',lon_0 = center[1],lat_0 = center[0],width = w*4000*0.81,height = h*4000*0.81, resolution = "i")
            m.drawcoastlines(color='yellow')
            m.drawcountries(color='yellow')

            im = plt.imshow(rotated_img, cmap='gray', extent=(*plt.xlim(), *plt.ylim()))
            
            plt.savefig(destFileRot, bbox_inches='tight', dpi=1000)

            img = misc.imread(destFileRot)
            img = img[109:-109,109:-109,:]
            img = misc.imresize(img, rimg.shape)
            if 90 < (rot%360) < 270:
                img = ndimage.rotate(img, -1 * (rot%180))
            else:
                img = ndimage.rotate(img, -1 * rot)
            
            rf = int((img.shape[0]/2) - oim.shape[0]/2)
            re = int((img.shape[0]/2) + oim.shape[0]/2)
            cf = int((img.shape[1]/2) - oim.shape[1]/2)
            ce = int((img.shape[1]/2) + oim.shape[1]/2)
            img = img[rf:re,cf:ce]

            img = Image.fromarray(img)

            try:
                img.save(destFileNoRot)
            except:
                logging.error('Image reverse rotation failed')

        elif cartopyPresent:

            def add_m(center, dx, dy):
                # source: https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters
                new_latitude  = center[0] + (dy / 6371000.0) * (180 / np.pi)
                new_longitude = center[1] + (dx / 6371000.0) * (180 / np.pi) / np.cos(center[0] * np.pi/180)
                return [new_latitude, new_longitude]

            fig = plt.figure()

            img = ndimage.rotate(im, rot)
            rimg = img[:]

            dx = img.shape[0]*4000/2*0.81 # in meters
            dy = img.shape[1]*4000/2*0.81 # in meters

            leftbot = add_m(center, -1*dx, -1*dy)
            righttop = add_m(center, dx, dy)

            img_extent = (leftbot[1], righttop[1], leftbot[0], righttop[0])

            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.imshow(img, origin='upper', cmap='gray', extent=img_extent, transform=ccrs.PlateCarree())
            ax.coastlines(resolution='50m', color='yellow', linewidth=1)
            ax.add_feature(cartopy.feature.BORDERS, linestyle='-', edgecolor='yellow')

            plt.savefig(destFileRot, bbox_inches='tight', dpi=1000)

            img = misc.imread(destFileRot)
            img = img[109:-109,109:-109,:]
            img = misc.imresize(img, rimg.shape)
            if 90 < (rot%360) < 270:
                img = ndimage.rotate(img, -1 * (rot%180))
            else:
                img = ndimage.rotate(img, -1 * rot)
            
            rf = int((img.shape[0]/2) - oim.shape[0]/2)
            re = int((img.shape[0]/2) + oim.shape[0]/2)
            cf = int((img.shape[1]/2) - oim.shape[1]/2)
            ce = int((img.shape[1]/2) + oim.shape[1]/2)
            img = img[rf:re,cf:ce]

            img = Image.fromarray(img)
            try:
                img.save(destFileNoRot)
            except:
                logging.error('Image reverse rotation failed')


    @property
    def getImage(self):

        '''Get the image from data

        Returns:
            :obj:`numpy array`: A matrix of pixel values
        '''

        if self.__image is None:
            if self.__audOut is None or self.__syncA is None or self.__syncB is None:
                self.getCrudeSync()

            logging.info('Beginning image extraction')
            
            # get audio
            amSig = self.__audOut

            # apply a bandpass filter to remove any noise
            amSig.filter(filters.butter(amSig.sampRate, 400, 4400, typeFlt = constants.FLT_BP, zeroPhase = True))

            # am demodulate
            amSig = self.__getAM(amSig)

            # convert sync from samples to time
            csyncA = self.__syncA / self.__syncCrudeSampRate
            csyncB = self.__syncB / self.__syncCrudeSampRate

            # convert back to sample number
            csyncA *= amSig.sampRate
            csyncB *= amSig.sampRate

            # store uncorrected csync
            ucsync = csyncA[:]

            # correct any missing syncs
            csyncA = self.__fillSync(csyncA, amSig.length)
            csyncB = self.__fillSync(csyncB, amSig.length)

            # we want channel A first always
            if csyncB[0] < csyncA[0]:
                csyncB.pop(0)

            if csyncB[-1] < csyncA[-1]:
                csyncA.pop(-1)

            if not len(csyncA) == len(csyncB):
                logging.error("Number of syncA and syncB unequal")
                csyncB = np.array(csyncA) +  int(0.25 * amSig.sampRate)

            self.__image = []
            imageBuffer = []
            backupImage = []

            numPixels = int(0.5/constants.NOAA_T)
            imgLine = amSig.signal[:int(len(amSig.signal)/numPixels) * numPixels]
            imgLine = np.reshape(imgLine, (numPixels, int(len(imgLine)/numPixels)))
            imgLine = np.median(imgLine, axis = -1)
            (self.__low, self.__high) = np.percentile(imgLine, (0.5, 99.5))

            # vars for image correction
            lowFifo, highFifo = [], []
            corrfifo = []
            corrfifosig = []
            corrfifosig2 = []
            ncorrfifo = 3
            lcorr = None
            lcorrsig = None
            statecorr = 0
            valuesPixCorr = []
            valuesSigCorr = []
            self.__slope = None
            self.__intercept = None
            chidFifo1 = []
            chidFifo2 = []

            for syncIndex in range(len(csyncA)):

                logging.info('Decoding line %d of %d lines', syncIndex + 1, len(csyncA))

                startIA = int(csyncA[syncIndex])
                startIB = int(csyncB[syncIndex])

                endIA = startIB
                endIB = startIB + int(0.25 * amSig.sampRate)
                if 1+syncIndex < len(csyncA):
                    endIB = int(csyncA[syncIndex + 1])
                    
                if endIB > amSig.length or endIA > amSig.length or startIA < 0 or startIB < 0:
                    continue

                imgLineA = amSig.signal[startIA:endIA]
                imgLineB = amSig.signal[startIB:endIB]


                imgLineA = signal.resample(imgLineA, int(int(len(imgLineA)/(numPixels*0.5)) * (numPixels*0.5)))
                imgLineB = signal.resample(imgLineB, int(int(len(imgLineB)/(numPixels*0.5)) * (numPixels*0.5)))

                imgLineA = np.reshape(imgLineA, (int(numPixels*0.5), int(len(imgLineA)/(numPixels*0.5))))
                imgLineB = np.reshape(imgLineB, (int(numPixels*0.5), int(len(imgLineB)/(numPixels*0.5))))

                # image color correction based on sync
                if csyncA[syncIndex] in ucsync:
                    for j in range(len(constants.NOAA_SYNCA)):
                        if constants.NOAA_SYNCA[j] == 0:
                            lowFifo.extend(imgLineA[j])
                        else:
                            highFifo.extend(imgLineA[j])
                        lowFifo = lowFifo[-1*constants.NOAA_COLORCORRECT_FIFOLEN:]
                        highFifo = highFifo[-1*constants.NOAA_COLORCORRECT_FIFOLEN:]
                    val11, val244 = np.median(lowFifo), np.median(highFifo)
                    val0 = val11 - (val244 - val11)*(11 - 0)/(244 - 11)
                    val255 = val11 - (val244 - val11)*(11 - 255)/(244 - 11)
                    self.__low = val0
                    self.__high = val255

                # image color correction based on calibration strip
                lengthOfStrip = int((len(constants.NOAA_SYNCA) * constants.NOAA_T) * amSig.sampRate)
                stripVal = np.median(amSig.signal[startIA - lengthOfStrip:startIA])

                corrfifo.append(255 * (stripVal - self.__low) / (self.__high - self.__low))
                corrfifo = corrfifo[-1*ncorrfifo:]
                outcorr = np.median(corrfifo)
                
                corrfifosig.append(stripVal)
                corrfifosig = corrfifosig[-1*ncorrfifo:]
                outcorrsig = np.median(corrfifosig)

                lengthOfStrip2 = int((len(constants.NOAA_SYNCB) * constants.NOAA_T) * amSig.sampRate)
                stripVal2 = np.median(amSig.signal[startIB - lengthOfStrip2:startIB])

                corrfifosig2.append(stripVal2)
                corrfifosig2 = corrfifosig2[-1*ncorrfifo:]
                outcorrsig2 = np.median(corrfifosig2)

                chidFifo1.append(outcorrsig2)
                chidFifo1 = chidFifo1[-100:]

                chidFifo2.append(outcorrsig)
                chidFifo2 = chidFifo2[-100:]

                if lcorr is None or abs(outcorr - lcorr) > 255.0/16:
                    logging.info('Color correction state: %d', statecorr)
                    if statecorr == 0 and not lcorrsig is None:
                        valuesPixCorr = [lcorr, outcorr]
                        valuesSigCorr = [lcorrsig, outcorrsig]
                        statecorr = 1
                    elif 1 <= statecorr <= 6:
                        if outcorr - valuesPixCorr[-1] > 2*255.0/(8*3):
                            valuesPixCorr.append(outcorr)
                            valuesSigCorr.append(outcorrsig)
                            statecorr += 1
                        else:
                            statecorr = 0
                    elif statecorr == 7:
                        if valuesPixCorr[-1] - outcorr > 2*255.0/3:
                            valuesPixCorr = [outcorr] + valuesPixCorr
                            valuesSigCorr = [outcorrsig] + valuesSigCorr
                            self.__slope, self.__intercept, r_value, p_value, std_err = stats.linregress(valuesSigCorr,np.array([i for i in range(9)]) * 255.0/8)
                            logging.info('Color correction bingo slope: %f intercept: %f', self.__slope, self.__intercept)
                            if len(chidFifo1) > 1+64+8:
                                    self.__chIDA = int(np.round((self.__slope*np.median(chidFifo1[-1-64-8:-1-64]) + self.__intercept) / (255.0/8)))
                                    self.__chIDB = int(np.round((self.__slope*np.median(chidFifo2[-1-64-8:-1-64]) + self.__intercept) / (255.0/8)))

                            chidFifo1 = []
                            chidFifo2 = []
                            statecorr = 0
                        else:
                            statecorr = 0
                lcorr = outcorr
                lcorrsig = outcorrsig


                imgLineA = np.median(imgLineA, axis = -1)
                imgLineB = np.median(imgLineB, axis = -1)
                imgLine = np.concatenate([imgLineA, imgLineB])

                if self.__slope is None or self.__intercept is None:
                    imageBuffer.append(imgLine[:])
                    imgLine = np.round(255 * (imgLine - self.__low) / (self.__high - self.__low))
                    imgLine[imgLine < 0] = 0
                    imgLine[imgLine > 255] = 255
                    imgLine = imgLine.astype(np.uint8)
                    backupImage.append(imgLine)
                else:
                    if len(imageBuffer) > 0:
                        for i in imageBuffer:
                            imgLineb = np.round(i*self.__slope + self.__intercept)
                            imgLineb[imgLineb < 0] = 0
                            imgLineb[imgLineb > 255] = 255
                            imgLineb = imgLineb.astype(np.uint8)
                            self.__image.append(imgLineb)
                        imageBuffer = []
                    imgLine = np.round(imgLine*self.__slope + self.__intercept)
                    imgLine[imgLine < 0] = 0
                    imgLine[imgLine > 255] = 255
                    imgLine = imgLine.astype(np.uint8)
                    self.__image.append(imgLine)

            # use backup if color correction didnot work
            if len(self.__image) == 0:
                self.__image = backupImage

            # get mean lengths of lines
            lens = [len(i) for i in self.__image]
            acceptedLen = max(set(lens), key=lens.count)
            self.__image = np.array([i for i in self.__image if len(i) == acceptedLen])

            logging.info('Image extraction complete')

        return self.__image

    def __fillSync(self, csync, maxLen):
        '''Filters and fills missed syncs to help generate image
        
        Args:
            csync (:obj:`list`): List of detected syncs
            maxLen (:obj:`int`): Frequency offset of source in Hz
        
        Returns:
            :obj:`list`: corrected syncs
        '''
        syncDIff = np.diff(csync)
        modeSyncDIff = max(set(syncDIff), key=list(syncDIff).count)
        wiggleRoom = 200

        validSyncs = []
        for i in range(len(csync) - 1):
            if abs(csync[i+1] - csync[i] - modeSyncDIff) < wiggleRoom:
                if csync[i] not in validSyncs:
                    validSyncs.append(csync[i])
                if csync[i+1] not in validSyncs:
                    validSyncs.append(csync[i+1])

        correctedSyncs = validSyncs[:]

        # initial correction
        c = validSyncs[0] - modeSyncDIff
        while(c > wiggleRoom):
            correctedSyncs.append(c)
            c -= modeSyncDIff

        # later corrections
        anchor = 0
        c = modeSyncDIff
        while(validSyncs[anchor] + c < maxLen):
            if (anchor + 1) < len(validSyncs) and (abs(validSyncs[anchor + 1] - c - validSyncs[anchor]) < wiggleRoom or c + validSyncs[anchor] > validSyncs[anchor + 1]):
                anchor += 1
                c = modeSyncDIff
            else:
                correctedSyncs.append(validSyncs[anchor] + c)
                c += modeSyncDIff

        return list(np.sort(correctedSyncs))

    @property
    def getImageA(self):
        '''Get Image A from the extracted image

        Returns:
            :obj:`numpy array`: A matrix list of pixel
        '''

        if self.__image is None:
            self.getImage

        return self.__image[:,:1040]

    @property
    def getImageB(self):
        '''Get Image B from the extracted image

        Returns:
            :obj:`numpy array`: A matrix list of pixel
        '''

        if self.__image is None:
            self.getImage

        return self.__image[:,1040:]

    @property
    def getColor(self):
        '''Get false color image (EXPERIMENTAL)

        Returns:
            :obj:`numpy array`: A matrix list of pixel
        '''

        if self.__color is None:
            if self.__image is None:
                self.getImage

            imageA = self.getImageA
            imageB = self.getImageB
            #imageAb = scipy.ndimage.uniform_filter(self.getImageA, size=(3, 3))
            #imageBb = scipy.ndimage.uniform_filter(self.getImageB, size=(3, 3))

            # constants
            #tempLimit = 147.0
            #seaLimit = 25.0
            #landLimit = 90.0

            #orig
            tempLimit = 155.0
            seaLimit = 30.0
            landLimit = 90.0

            colorImg = []
            for r in range(len(imageA)):
                colorRow = []
                for c in range(1040):
                    v, t = imageA[r,c], imageB[r,c]
                    #vb, tb = imageAb[r,c], imageBb[r,c]
                    maxColor, minColor = None, None
                    scaleVisible, scaleTemp = None, None
                    # change to >
                    if t < tempLimit:
                        # clouds
                        minColor, maxColor = [230/360.0, 0.2, 0.3], [230/360.0, 0.0, 1.0]
                        scaleVisible = v / 256.0
                        scaleTemp = (256.0 - t) / 256.0
                    else:
                        if v < seaLimit:
                            # sea
                            minColor, maxColor = [200.0/360.0, 0.7, 0.6], [240.0/360.0, 0.6, 0.4]
                            scaleVisible = v / seaLimit
                            scaleTemp = (256.0-t) / (256.0 - tempLimit)
                        else:
                            # ground
                            minColor, maxColor = [60.0/360.0, 0.6, 0.2], [100.0/360.0, 0.0, 0.5]
                            scaleVisible = (v - seaLimit) / (landLimit - seaLimit)
                            scaleTemp = (256.0 - t) / (256.0 - tempLimit);

                    finalS = maxColor[1] + scaleTemp * (minColor[1] - maxColor[1]);
                    finalV = maxColor[2] + scaleVisible * (minColor[2] - maxColor[2]);
                    finalH = maxColor[0] + scaleVisible * scaleTemp * (minColor[0] - maxColor[0]);
                    pix = tuple([int(k * 255.0) for k in colorsys.hsv_to_rgb(finalH, finalS, finalV)])
                    colorRow.append(pix)

                colorImg.append(colorRow)
            self.__color = np.uint8(np.array(colorImg))

        return self.__color

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
        fmDemdulator = demod_fm.demod_fm()
        chunkerObj = chunker.chunker(self.__sigsrc)

        for i in chunkerObj.getChunks:

            logging.info('Processing chunk %d of %d chunks', chunkerObj.getChunks.index(i)+1, len(chunkerObj.getChunks))

            sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(*i), chunkerObj).offsetFreq(self.__offset).filter(bhFilter).bwLim(self.__bw, uniq = "First").funcApply(fmDemdulator.demod).bwLim(audioFreq, strictness)
            audioOut.extend(sig)

        logging.info('FM demodulation successfully complete')
        self.__audOut = audioOut

        return audioOut

    def __getAM(self, sig):

        '''Do AM demodulation in chunks of given signal

        Args:
            sig (:obj:`comm object`): Input signal

        Returns:
            :obj:`commSignal`: AM demodulated signal
        '''

        logging.info('Beginning AM demodulation in chunks')

        amDemdulator = demod_am.demod_am()
        amOut = comm.commSignal(sig.sampRate)

        chunkerObj = chunker.chunker(sig, chunkSize = 60000*4)

        for i in chunkerObj.getChunks:

            logging.info('Processing chunk %d of %d chunks', chunkerObj.getChunks.index(i)+1, len(chunkerObj.getChunks))
            demodSig = amDemdulator.demod(sig.signal[i[0]:i[1]])
            amOut.extend(comm.commSignal(sig.sampRate, demodSig))

        logging.info('AM demodulation completed')

        return amOut

    def __correlate(self, haystack, needle):

        '''Function to do normalised correlation
        
        Args:
            haystack (:obj:`numpy array`): Input signal
            needle (:obj:`numpy array`): Sync signal

        Returns:
            :obj:`numpy array`: correlation array
        '''

        cor = signal.correlate(haystack, needle, mode = 'same')
        sums = np.convolve(haystack * haystack, [1]*len(needle), mode = 'same')
        norm = cor / (sums * np.sum(needle * needle))**0.5

        return norm

    def __correlateAndFindPeaks(self, sig, sync, getExtraInfo = False, useNormCorrelate = True, useFilter = False, usePosNeedle = True, filterType = filters.hamming(492, zeroPhase = True)):

        '''Correlates given signal and sync signal to find location of syncs

        Args:
            sig (:obj:`comm object`): Input signal
            sync (:obj:`list`): Sync bits

        Returns:
            :obj:`list`: List of detected syncs
        '''

        # create the sync signals, at required sampling frequency
        sampRateCorrection = round(sig.sampRate * constants.NOAA_T)
        if usePosNeedle:
            sync = ((np.repeat(sync, sampRateCorrection) * 233) + 11)/255
        else:
            sync = np.repeat(sync, sampRateCorrection) - 0.5

        # uncomment below if exact sampling frequency is desired
        #sync = signal.resample(sync, int(sig.sampRate * len(sync)/(sampRateCorrection*1.0/constants.NOAA_T)))

        # correlate signal with syncs
        cor = None
        if not useNormCorrelate:
            if useFilter:
                cor = signal.correlate(filterType.applyOn(sig.signal), sync, mode = 'same')
            else:
                cor = signal.correlate(sig.signal, sync, mode = 'same')
        else:
            if useFilter:
                cor = np.array(self.__correlate(filterType.applyOn(sig.signal), sync))
            else:
                cor = np.array(self.__correlate(sig.signal, sync))

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

        # offset it to the beginning of the sync
        absolutePeaks = [i - int(len(sync)/2) for i in absolutePeaks]

        absolutePeaks = np.sort(np.array(absolutePeaks).ravel())

        # get time sync values
        timeSyncs = []
        pkHeights = []
        if getExtraInfo:
            for i in absolutePeaks:
                if i+2*int(len(sync)) < sig.length:
                    timeSyncs.append(np.average(sig.signal[i+int(len(sync)):i+2*int(len(sync))]))
                else:
                    timeSyncs.append(None)
                pkHeights.append(cor[i + int(len(sync)/2)])

        if getExtraInfo:
            return absolutePeaks, pkHeights, timeSyncs

        return absolutePeaks
        
    def getCrudeSync(self):

        '''Get the sync locations: at constants.NOAA_CRUDESYNCSAMPRATE sampling rate

        Returns:
            :obj:`list`: A list of locations of sync in sample number (start of sync)
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

            # determine if some data was found or not
            syncAdiff = np.abs(np.diff(self.__syncA) - (self.__syncCrudeSampRate*0.5))
            minSyncAdiff = np.min([np.max(syncAdiff[i:i+constants.NOAA_DETECTCONSSYNCSNUM]) for i in range(len(syncAdiff)-constants.NOAA_DETECTCONSSYNCSNUM+1)])

            syncBdiff = np.abs(np.diff(self.__syncB) - (self.__syncCrudeSampRate*0.5))
            minSyncBdiff = np.min([np.max(syncBdiff[i:i+constants.NOAA_DETECTCONSSYNCSNUM]) for i in range(len(syncBdiff)-constants.NOAA_DETECTCONSSYNCSNUM+1)])

            if minSyncAdiff < constants.NOAA_DETECTMAXCHANGE or minSyncBdiff < constants.NOAA_DETECTMAXCHANGE:
                logging.info('NOAA Signal was found')
                self.__useful = 1
            else:
                logging.info('NOAA Signal was not found')

        return [self.__syncA, self.__syncB]

    def getAccurateSync(self, useNormCorrelate = True):

        '''Get the sync locations: at highest sampling rate

        Args:
            useNormCorrelate (:obj:`bool`, optional): Whether to use normalized correlation or not

        Returns:
            :obj:`list`: A list of locations of sync in sample number (start of sync)
        '''

        if self.__asyncA is None or self.__asyncB is None or self.__asyncBtime is None or self.__asyncAtime is None or self.__asyncBpk is None or self.__asyncApk is None or not self.__useNormCorrelate == useNormCorrelate:
            self.__useNormCorrelate = useNormCorrelate

            if self.__syncA is None or self.__syncB is None:
                self.getCrudeSync()

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
            self.__asyncApk = []
            self.__asyncAtime = []
            logging.info('Beginning Accurate SyncA detection')

            for i in csyncA:

                logging.info('Detecting Sync %d of %d syncs', list(csyncA).index(i) + 1, len(csyncA))

                startI = int(i) - int(searchSampleWidth)
                endI = int(i) + int(searchSampleWidth)
                if startI < 0 or endI > self.__sigsrc.length:
                    continue
                sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(startI, endI)).offsetFreq(self.__offset).filter(filters.blackmanHarris(151, zeroPhase = True)).funcApply(demod_fm.demod_fm().demod).funcApply(demod_am.demod_am().demod)
                syncDet, PkHeights, TimeSync = self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCA, getExtraInfo = True, useNormCorrelate = useNormCorrelate, usePosNeedle = useNormCorrelate, useFilter = True)
                self.__asyncA.append(syncDet[0] + startI)
                self.__asyncApk.append(PkHeights[0])
                self.__asyncAtime.append(TimeSync[0])
            logging.info('Accurate SyncA detection complete')

            ## Accurate syncB
            self.__asyncB = []
            self.__asyncBpk = []
            self.__asyncBtime = []
            logging.info('Beginning Accurate SyncB detection')

            for i in csyncB:

                logging.info('Detecting Sync %d of %d syncs', list(csyncB).index(i) + 1, len(csyncB))

                startI = int(i) - int(searchSampleWidth)
                endI = int(i) + int(searchSampleWidth)
                if startI < 0 or endI > self.__sigsrc.length:
                    continue
                sig = comm.commSignal(self.__sigsrc.sampFreq, self.__sigsrc.read(startI, endI)).offsetFreq(self.__offset).filter(filters.blackmanHarris(151, zeroPhase = True)).funcApply(demod_fm.demod_fm().demod).funcApply(demod_am.demod_am().demod)
                syncDet, PkHeights, TimeSync = self.__correlateAndFindPeaks(sig, constants.NOAA_SYNCB, getExtraInfo = True, useNormCorrelate = useNormCorrelate, usePosNeedle = useNormCorrelate, useFilter = True)
                self.__asyncB.append(syncDet[0] + startI)
                self.__asyncBpk.append(PkHeights[0])
                self.__asyncBtime.append(TimeSync[0])
            logging.info('Accurate SyncB detection complete')

        return [self.__asyncA, np.diff(self.__asyncA), self.__asyncApk, self.__asyncAtime, self.__asyncB, np.diff(self.__asyncB), self.__asyncBpk, self.__asyncBtime]


