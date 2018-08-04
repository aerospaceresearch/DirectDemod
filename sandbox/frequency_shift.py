import numpy as np
from scipy import fft
import matplotlib.pylab as plt

def make_fft(window, samplerate, df, every, iq_stream):

    result_of_fft = []

    counting_until_every_reached = 0

    adc_offset = -127
    # bringing the signal per kernel down around the average reduces the dc peak at f=0hz!
    # either by offset or directly by casting as uint int :)

    for slice in range(0 , len(iq_stream) , window*2):
        iq_stream_slice = (adc_offset + iq_stream[slice: slice + window * 2: 2]) + 1j * (adc_offset + iq_stream[slice + 1: slice + window * 2: 2])

        # if wav, i and q is different than it is for binary format
        # iq_stream_slice = (offset + test[s+1: s+window*2: 2]) + 1j*(offset + test[s: s+window*2: 2])

        iq_stream_slice_intensity = np.abs(fft(iq_stream_slice))
        del iq_stream_slice

        counting_until_every_reached += 1
        if slice == 0:
            iq_stream_slice_overlay = iq_stream_slice_intensity# / np.max(g)
        else:
            if len(iq_stream_slice_intensity) == window: # in case the recorded stream cannot be fully parted
                iq_stream_slice_overlay = iq_stream_slice_overlay + iq_stream_slice_intensity# / np.max(g)

        if counting_until_every_reached >= every:#reduce amount of plot here
            #iq_stream_slice_overlay = iq_stream_slice_overlay
            yplot = 1.0/window * (np.fft.fftshift(iq_stream_slice_overlay))
            #print(yplot)
            yplot = yplot / every
            #print(yplot)
            #print(np.max(yplot), np.mean(yplot))
            result_of_fft.append(np.log(yplot))
            counting_until_every_reached = 0
            iq_stream_slice_overlay = 0

        del iq_stream_slice_intensity

    return result_of_fft

def rolling_window(input, window):
    output = []

    for i in range(len(input)):
        if i < window // 2:
            output.append(np.mean(input[0 : window]))
        elif i > len(input) - window // 2:
            output.append(np.mean(input[-window // 2 : ]))
        else:
            output.append(np.mean(input[i - window // 2 : i - window // 2 + window]))

    return output


def find_shift(iq_stream, samplerate, center_frequency, channel_frequency, bandwidth):

    window = 2048*2*2
    #http://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
    # sample spacing
    T = 1.0 / samplerate
    x = np.linspace(0.0, window*T, window)

    xf = np.fft.fftfreq(window, T)
    xf = np.fft.fftshift(xf)

    df = xf[1]-xf[0]

    every = (len(iq_stream) / (samplerate * 2.0)) * 8192.0 / (window)
    result = make_fft(window, samplerate, df, every, iq_stream)


    center = (samplerate / 2 + (channel_frequency - center_frequency)) / df
    band_start = int(center - bandwidth/(2*df))
    band_stop = int(center + bandwidth/(2*df))

    result_band = []
    for i in range(len(result)):
        result_band.append(result[i][band_start:band_stop])

    #plt.imshow(result_band, interpolation='nearest')
    #plt.imshow(result)
    #plt.gca().invert_yaxis()
    #plt.gca().invert_xaxis()
    #plt.gca().set_xticks(xf)
    #plt.show()

    track = []
    for i in range(len(result_band)):
        result_band[i] = np.subtract(result_band[i], np.min(result_band[i]))
        track.append(np.argmax(result_band[i]) - bandwidth/(2*df))



    #plt.imshow(result_band, interpolation='nearest')
    #plt.imshow(result)
    #plt.gca().invert_yaxis()
    #plt.gca().invert_xaxis()
    #plt.gca().set_xticks(xf)
    #plt.show()

    N = int(len(track)*0.1)
    track = np.multiply(rolling_window(track, N), df)

    frequency_shift_mean = np.mean(track)
    frequency_shift_max = np.max(track)
    frequency_shift_min = np.min(track)

    #print(frequency_shift_max, frequency_shift_mean, frequency_shift_min)

    for i in range(len(result_band)):
        result_band[i][int(track[i]/df + bandwidth/(2*df))] = 0

    #plt.imshow(result_band, interpolation='nearest')
    #plt.imshow(result)
    #plt.gca().invert_yaxis()
    #plt.gca().invert_xaxis()
    #plt.gca().set_xticks(xf)
    #plt.show()


    return track

def correct_shift(shift, position):
    step = 1/(len(shift)-1)
    x1 = int(np.floor(position / step + (step / 2)))

    '''
    x2 = int(np.ceil(position / step + (step / 2)))

    m = (shift[x2] - shift[x1]) / (x2 - x1)
    b = shift[x1] - m*x1

    print((position / step + (step / 2)), m, b)

    y = m * (position / step + (step / 2)) + b
    '''

    y = shift[x1]
    return y


def correct(iq_stream, samplerate, center_frequency, channel_frequency, bandwidth, chunk_number, chunk_length):
    shift = find_shift(iq_stream, samplerate, center_frequency, channel_frequency, bandwidth)
    return correct_shift(shift, chunk_number / chunk_length)


if __name__ == "__main__":

    # need the stream as serial binary data. no complex.
    iq_streama = np.memmap("D:/rx/rx/fun_2018-07-30T064300Z_2018-07-30T065400Z_1234512345_5.dat")

    center_frequency = 145865000
    channel_frequency = 145938200
    samplerate = 2048000
    bandwidth = 20000 # the bandwidth must cover the signal to be able to find it.

    # from the current signal chunk
    chunk_number = 5
    chunk_length = 10

    print("doppler shift is",
          correct(iq_streama, samplerate, center_frequency, channel_frequency, bandwidth, chunk_number, chunk_length),
          "Hz")