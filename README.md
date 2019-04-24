# DirectDemod
Direct Demodulation of Radio-signals

## Decoders
* NOAA images (Under progress)
* AFSK1200 (Under progress)

## Run example
To run: run 'python main.py IQ.wav'

(using Docker)
```
sudo docker build --tag direct_demod .
sudo docker run --rm -it \
   --volume="$PWD":/opt/code \
   direct_demod python main.py samples/SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav
```

## Install

### Linux

You can install DirectDemod on linux, using the `install.sh` script. Steps are given below.

1. Change the mode of file, to make it executable. `sudo chmod +x ./install`.

2. Execute the file using sudo only. `sudo ./install`.

## Documentation
Please find the docs at: [directdemod.readthedocs.io](https://directdemod.readthedocs.io)

## Experiments
The experiments performed to make design decisions are in the folder experiments, as jupyter notebooks. (click the binder badge for an online version)

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/aerospaceresearch/DirectDemod/Vinay_dev)[![Documentation Status](https://readthedocs.org/projects/directdemod/badge/?version=vinay_dev)](http://directdemod.readthedocs.io/en/vinay_dev/?badge=vinay_dev)
