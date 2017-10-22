[![Build Status](https://travis-ci.org/aerospaceresearch/DirectDemod.svg)](https://travis-ci.org/aerospaceresearch/DirectDemod)

# DirectDemod
direct demodulation of radio-signals

# run example

(using Docker)

```
docker build --tag direct_demod .
docker run --rm -ti -v `pwd`:/opt/code direct_demod python main.py samples/SDRSharp_20170830_073907Z_145825000Hz_IQ_autogain.wav
```
