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

## Install with `conda`


To install package with conda you should install anaconda or miniconda distribution first.
See installation: https://docs.conda.io/en/latest/miniconda.html.

When conda is installed, clone the repository and create conda a new conda environment. (To keep different versions of your packages of different project from interfering with each other)

```
git clone https://github.com/aerospaceresearch/DirectDemod
cd DirectDemod/
conda create -n env_name
conda activate env_name (or source activate env_name, if the previous doesn't work, In some environments, it might be deprecated)
conda config --add channels conda-forge
conda install --file requirements.txt

```

You should add `directdemod` package to your `PYTHONPATH`. 
<br>
On Windows edit environment variable `PYTHONPATH` and append path to DirectDemod directory to it.
On Linux edit `.bashrc`:

```
export PYTHONPATH=$PYTHONPATH:/path/to/DirectDemod
```

Update `.bashrc`.

```
source ~/.bashrc
```

### Test installation

To test installation, run the following command (from `DirectDemod` directory). You should see, that all
tests were passed successfully. Occasional warnings are ok.

```
pytest
```

## Documentation
Please find the docs at: [directdemod.readthedocs.io](https://directdemod.readthedocs.io)

## Experiments
The experiments performed to make design decisions are in the folder experiments, as jupyter notebooks. (click the binder badge for an online version)

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/aerospaceresearch/DirectDemod/Vinay_dev)[![Documentation Status](https://readthedocs.org/projects/directdemod/badge/?version=vinay_dev)](http://directdemod.readthedocs.io/en/vinay_dev/?badge=vinay_dev)
