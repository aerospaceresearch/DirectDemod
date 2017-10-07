import os
import sys

import numpy as np


def loading_file(filename):

    if filename.find(".wav") > -1:
        # for example for SDR# sharp baseline recordings
        signal = np.memmap(filename, offset=44)

    elif filename.find(".dat") > -1:
        # for example for RTLSDR raw recordings
        signal = np.memmap(filename, offset=0)

    return signal


# loading in the iq imput file
# adjusting the uint values by -127 to match the recorded IQ values to reality
if len(sys.argv) == 1:
    filename = os.path.join("samples", "earth_aprs1200_1signal_1peak_SDRSharp_20170816_105454Z_144800000Hz_IQ.wav")
else:
    filename = sys.argv[1]

signal = loading_file(filename)
signal = -127 + signal[:]


# converting signal to complex signal, but chunkwise
samplerate = 2048000
chunk_period = 5
chunk_size = samplerate * 2 * chunk_period
frequency_offset = 0

for chunk in range(0, len(signal), chunk_size):
    signal_chunk = signal[chunk + 0 : chunk + chunk_size : 2] + 1j*signal[chunk + 1 : chunk + chunk_size : 2]

    # in case you think there could be a doppler shift or you commanded an frequency offset for the recording
    # you can correct the shift in frequency with the following digital complex expontential
    frequency_correction = np.exp(-1.0j * 2.0 * np.pi * frequency_offset / samplerate * np.arange(len(signal_chunk)))

    # and multiply it with your signal
    signal_shifted = signal_chunk * frequency_correction

print("finished")
