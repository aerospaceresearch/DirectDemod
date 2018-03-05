[![Build Status](https://travis-ci.org/aerospaceresearch/DirectDemod.svg)](https://travis-ci.org/aerospaceresearch/DirectDemod)

# DirectDemod
Direct Demodulation of Radio-signals

## Run example

(using Docker)

```
sudo docker build --tag direct_demod .
sudo docker run --rm -it \
   --volume="$PWD":/opt/code \
   direct_demod python main.py samples/SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav
```
