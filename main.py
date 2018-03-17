import os
import sys
import time
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pylab as plt
from scipy.io.wavfile import write as sc_write


# inspired by
# https://github.com/osmocom/rtl-sdr/blob/master/src/rtl_fm.c
# thank you!


# Look up table size
atan_lut_size = 131072 # =512 kB
atan_lut_coeff = 8

def loading_file(filename):

    if filename.find(".wav") > -1:
        # for example for SDR# sharp baseline recordings
        signal = np.memmap(filename, offset=44)

    elif filename.find(".dat") > -1:
        # for example for RTLSDR raw recordings
        signal = np.memmap(filename, offset=0)

    return signal


def fm_demod(signal):
    # low-passing
    lp = low_pass(signal)
    lp_len = len(lp)  # must stay double the size of result, due to later for loop

    result = np.zeros(len(lp)//2)

    pcm = polar_discriminant(lp[0], lp[1], 0, 0)
    result[0] = int(pcm)

    for i in range(2, lp_len-1, 2):
        # being lazy, only case 0 for now...
        # there are other cases in rtl_fm.exe

        # case 0
        pcm = polar_discriminant(lp[i], lp[i + 1], lp[i - 2], lp[i - 1])

        result[i // 2] = int(pcm)

    pre_r = lp[lp_len - 2]
    pre_j = lp[lp_len - 1]
    # result_len = lp_len // 2
    return result


def multiply(ar, aj, br, bj):
    cr = ar * br - aj * bj
    cj = aj * br + ar * bj
    return cr, cj


def polar_discriminant(ar, aj, br, bj):
    cr, cj = multiply(ar, aj, br, -bj)
    angle = np.arctan2(cj, cr)
    return (angle / np.pi * (1 << 14))
    # return (angle * 180.0 / np.pi)


def fast_atan2(y, x):
    pi4 = (1 << 12)  # since pi = 1 << 14
    if(x == 0 and y == 0):
        return 0
    if(x >= 0):
        angle = pi4*(1 - (x-abs(y)) / (x+abs(y)))
    else:
        angle = pi4*(3 - (x+abs(y)) / (abs(y)-x))
    angle *= abs(y)/y
    return angle

def polar_disc_fast(ar, aj, br, bj):
    cr, cj = multiply(ar, aj, br, -bj)
    return fast_atan2(cj, cr)


def atan_lut():
    for i in range(0, atan_lut_size):
        atan_lut = np.arctan(i/((1 << atan_lut_coeff)*np.pi)*(1 << 14))

def polar_disc_lut(ar, aj, br, bj):
    atan_lut()
    cr, cj = multiply(ar, aj, br, -bj)
    # Special cases
    if cr == 0 and cj == 0:
        return 0
    elif cr == 0 and cj > 0:
        return 1 << 13
    elif cr == 0 and cj > 0:
        return -(1 << 13)
    elif cr > 0 and cj == 0:
        return 0
    elif cr < 0 and cj == 0:
        return 1 << 14
    # real range -32768 - 32768 use 64x range -> absolute maximum: 2097152
    x = (cj << atan_lut_coeff)/cr
    if abs(x) >= atan_lut_size:
        # can use linear range, but not necessary
        pdl = 1<<13 if cj > 0 else -1<<13
    else:
        if x > 0:
            pdl = atan_lut[x] if cj > 0 else atan_lut[x] - (1<<14)
        else:
            pdl = (1<<14) - atan_lut[-x] if cj > 0 else -atan_lut[-x]

    return pdl


def low_pass(signal):
    # simple square window FIR
    lowpassed = np.zeros(len(signal) // downsample*2)
    # needs to be go outside this function
    now_r = 0
    now_j = 0
    i = 0
    i2 = 0
    prev_index = 0
    while (i < len(signal)):
        now_r += signal[i]
        now_j += signal[i + 1]
        i += 2
        prev_index += 2
        if (prev_index < downsample):
            continue
        lowpassed[i2] = now_r
        lowpassed[i2 + 1] = now_j
        prev_index = 0
        now_r = 0
        now_j = 0
        i2 += 2
    # lp_len = i2
    return lowpassed


def deemph_filter(lowpassed):
    avg = 0
    d = 0
    lp = np.zeros(len(lowpassed))
    # de-emph IIR # avg = avg * (1 - alpha) + sample * alpha

    for i in range(0, len(lp), 1):
        d = lowpassed[i] - avg
        if (d > 0):
            avg += (d + deemph_a / 2) / deemph_a
        else:
            avg += (d - deemph_a / 2) / deemph_a

        lp[i] = avg

    return lp


def low_pass_real(input):
    # simple square window FIR

    i2 = 0
    i = 0

    fast = rate_out
    slow = rate_out2

    prev_lpr_index = 0
    now_lpr = 0

    result_len = len(input)
    result = []

    while i < result_len:

        now_lpr += input[i]
        i += 1
        prev_lpr_index += slow
        if prev_lpr_index < fast:
            continue

        result.append(now_lpr / (fast/slow))
        prev_lpr_index -= fast
        now_lpr = 0
        i2 += 1

    result_len = i2
    return result


if __name__ == '__main__':
    # all the inputs
    # # basics
    filename_sample = os.path.join("samples", "SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav")
    frequency_offset_sample = -1500.0

    # # input data conversion
    samplerate = 2048000
    chunk_period = 4
    chunk_size = samplerate * 2 * chunk_period
    frequency_offset = 0

    # # audio
    rate_in = 22050  # bandpass
    downsample = (samplerate // rate_in + 1) * 2
    capture_rate = rate_in * downsample
    rate_out = rate_in
    rate_out2 = 22050

    # now, let's start this and have some fun

    # # loading in the iq imput file
    # # adjusting the uint values by -127 to match the recorded IQ values to reality
    if len(sys.argv) == 1:
        filename = filename_sample
        frequency_offset = frequency_offset_sample
    else:
        filename = sys.argv[1]

    signal = loading_file(filename)
    signal = -127 + signal[:]

    # # converting signal to complex signal, but chunkwise
    for chunk in range(0, len(signal), chunk_size):
        signal_chunk = signal[chunk + 0: chunk + chunk_size: 2] + 1j*signal[chunk + 1: chunk + chunk_size: 2]

        if frequency_offset != 0.0:
            # in case you think there could be a doppler shift or you commanded an frequency offset for the recording
            # you can correct the shift in frequency with the following digital complex expontential
            frequency_correction = np.exp(-1.0j * 2.0 * np.pi * frequency_offset / samplerate * np.arange(len(signal_chunk)))

            # and multiply it with your signal
            signal_shifted = signal_chunk * frequency_correction
        else:
            signal_shifted = signal_chunk

        # now comes "the audio" part. it is inspired by the rtl_fm.exe.
        # for now, we downconvert. at a later point, we will keep the original sampling rate
        for i in range(0, len(signal_shifted), 1):
            # filling it back into the original variable.
            # keeps amput on mamory lower, but if we need to use the value again for another requency band, we need to
            # do that again. So there will be a to-do, to make this better, in THE FUTURE! ;)
            signal[chunk + i*2] = signal_shifted.real[i]
            signal[chunk + i*2 + 1] = signal_shifted.imag[i]

    signal_demod = fm_demod(signal)

    deemph_a = int(round(1.0 / ((1.0 - np.exp(-1.0 / (rate_out * 75e-6))))))
    signal_deemphed = deemph_filter(signal_demod)

    signal_final = low_pass_real(signal_deemphed)
    signal_final = np.array(signal_final, dtype=np.int16)

    # for all of us interesting to hear it beep
    sc_write("signal.wav", rate_out2, signal_final)

    # visual check of the demodulated output
    '''
    plt.plot(signal_demod, label="demod")
    plt.plot(signal_deemphed, label="deemphed")
    plt.plot(signal_final, label="final")
    plt.legend()
    plt.show()
    plt.savefig('signal.svg')
    '''

    # 1200 baud AFSK demodulator

    # # inspired by
    # # https://github.com/EliasOenal/multimon-ng/blob/master/demod_afsk12.c
    # # https://sites.google.com/site/wayneholder/attiny-4-5-9-10-assembly-ide-and-programmer/bell-202-1200-baud-demodulator-in-an-attiny10

    baudrate = 1200.0
    buffer_size = int(np.round(rate_out2 / baudrate))
    mark_frequency = 1200.0
    space_frequency = 2200.0

    # creating the “correlation list" for the comparison frequencies of the digital frequency filers
    corr_mark_i = np.zeros(buffer_size)
    corr_mark_q = np.zeros(buffer_size)
    corr_space_i = np.zeros(buffer_size)
    corr_space_q = np.zeros(buffer_size)

    # filling the "correlation list" with sampled waveform for the two frequencies.
    for i in range(buffer_size):
        mark_angle = (i * 1.0 / rate_out2) / (1 / mark_frequency) * 2 * np.pi
        corr_mark_i[i] = np.cos(mark_angle)
        corr_mark_q[i] = np.sin(mark_angle)

        space_angle = (i * 1.0 / rate_out2) / (1 / space_frequency) * 2 * np.pi
        corr_space_i[i] = np.cos(space_angle)
        corr_space_q[i] = np.sin(space_angle)

    # nornalizing the signal between -1 and +1
    signal_normalized = np.divide(signal_final, 2**15)

    # comparing the signal to the cosine and sine parts to both frequencies in the "correlation lists"
    binary_filter = np.zeros(len(signal_normalized))

    for sample in range(len(signal_normalized)-buffer_size):
        corr_mi = 0
        corr_mq = 0
        corr_si = 0
        corr_sq = 0

        for sub in range(buffer_size):
            corr_mi = corr_mi + signal_normalized[sample + sub] * corr_mark_i[sub]
            corr_mq = corr_mq + signal_normalized[sample + sub] * corr_mark_q[sub]

            corr_si = corr_si + signal_normalized[sample + sub] * corr_space_i[sub]
            corr_sq = corr_sq + signal_normalized[sample + sub] * corr_space_q[sub]

        binary_filter[sample] = (corr_mi ** 2 + corr_mq ** 2 - corr_si ** 2 - corr_sq ** 2)
        # binary_filter[sample] = np.sign(binary_filter[sample])

    binary_filter = np.sign(binary_filter)

    # visual check of the fm demodulated output
    plt.plot(binary_filter, label="binary filter")
    plt.plot(np.divide(signal_normalized, np.max(signal_normalized)), label="fm demodulated signal")
    plt.title("fm demodulated signal and binary filter")
    plt.legend()
    plt.show()

    # finding the starting flag
    starting_flag_start = [0, 1, 1, 1, 1, 1, 1]
    needle_start = []
    needle_small = []
    for i in range(len(starting_flag_start)):
        for j in range(buffer_size):
            if starting_flag_start[i] == 0:
                needle_start.append(-1)
            elif starting_flag_start[i] == 1:
                needle_start.append(1)

        if starting_flag_start[i] == 0:
            needle_small.append(-1)
        elif starting_flag_start[i] == 1:
            needle_small.append(1)

    time1 = time.time()
    correlation_start = np.divide(np.correlate(binary_filter, needle_start, mode="same"), len(needle_start))
    print("it took me", time.time() - time1, "seconds")

    # finding the positions of the starting flags
    starting_flag_positions = []
    time1 = time.time()
    for step in range(0, len(correlation_start) - len(needle_start), len(needle_start)):
        correlation_chunk = correlation_start[step: step + len(needle_start)]

        if np.max(correlation_chunk) >= 0.90:
            starting_flag_positions.append(step + np.argmax(correlation_chunk))

    print("it took me", time.time() - time1, "seconds")
    time1 = time.time()

    # filtering out the repetitions, that are to close to each other...
    starting_flag_found = []
    if len(starting_flag_positions) == 0:
        print("no flag, no start. sorry")

    elif len(starting_flag_positions) == 1:
        # lazy, need to fill this
        starting_flag_found.append(starting_flag_positions[0])
        print("only one starting flag found at", starting_flag_positions[0])

    elif len(starting_flag_positions) >= 2:
        flag_distance = 600  # just a gut feeling. works for me
        for flag in range(len(starting_flag_positions) - 1):
            if starting_flag_positions[flag + 1] - starting_flag_positions[flag] >= flag_distance:
                starting_flag_found.append(starting_flag_positions[flag])
                print("for starting flag #", flag, ", found the starting flag at position", starting_flag_positions[flag])

        if starting_flag_positions[-1] - starting_flag_positions[-2] >= flag_distance:
            starting_flag_found.append(starting_flag_positions[-1])
            print("found the starting flag at position", starting_flag_positions[-1])

    for flag in range(len(starting_flag_found)):
        # finding the end of the needle
        runner = 0
        while binary_filter[starting_flag_found[flag] + runner] == binary_filter[
                            starting_flag_found[flag] + runner + 1]:
            runner += 1

        # visual check again
        plt.plot(binary_filter[starting_flag_found[flag]: starting_flag_found[flag] + 500],
                 label="binary filter")
        plt.plot(correlation_start[starting_flag_found[flag]: starting_flag_found[flag] + 500],
                 label="correlation of starting flag over binary filter")
        plt.plot([runner], [1], "*", label="end of start flag")
        plt.title("each starting flag")
        plt.legend()
        plt.show()

        # updating the found start with the real start
        starting_flag_found[flag] = starting_flag_found[flag] + runner

    # visual check for full signal
    plt.plot(binary_filter, label="binary filter")
    plt.plot(correlation_start, label="correlation of starting flag over binary filter")
    plt.title("full binary filter of signal")
    plt.legend()
    plt.show()

    # making bits and bytes
    for flag in range(len(starting_flag_found)):
        nrzi = []
        nrzi_quality = []

        # synch to the first pullup
        start = 2
        while binary_filter[starting_flag_found[flag] + start] != 1:
            start += 1

        step = 0
        runner = 0
        correlation_sum = 0
        while step < 3000 and correlation_sum < len(needle_small):
            bit_quality = np.mean(binary_filter[starting_flag_found[flag] + start + runner:
                                                starting_flag_found[flag] + start + runner + buffer_size])
            bit_quality_next = np.mean(binary_filter[starting_flag_found[flag] + start + runner + buffer_size:
                                                     starting_flag_found[flag] + start + runner + buffer_size * 2])
            # print(step, np.sign(bit_quality), bit_quality, runner)
            nrzi.append(np.sign(bit_quality))
            nrzi_quality.append(bit_quality)

            if len(nrzi) >= 7:
                correlation_sum = np.max(np.correlate(nrzi[-8: -1], needle_small, mode="same"))

            if np.sign(bit_quality) < np.sign(bit_quality_next):
                # print("synching step at step", step)
                runner += buffer_size // 2
                while binary_filter[starting_flag_found[flag] + start + runner] != 1:
                    runner += 1

            else:
                runner += buffer_size

            step += 1

        plt.plot(binary_filter[starting_flag_found[flag]: starting_flag_found[flag] + buffer_size * 100], label="binary filter")
        plt.plot([start], [1], "*", label="start of NRZI")
        plt.title("start of NRZI signal")
        plt.legend()
        plt.show()

        correlation_end = np.correlate(nrzi, needle_small, mode="same")
        plt.plot(nrzi, label="nrzi bits")
        plt.plot(correlation_end, label="nrzi correlation to frame end flag")
        plt.title("NRZI bits and its end")
        plt.legend()
        plt.show()

        print("for starting flag #", flag, ", this is your non-return-to-zero-inverted code", nrzi)

    print("finished, for now")
