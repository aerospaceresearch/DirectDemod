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

**Note.** If you install with pip, then to use georeferencer you will have 
to install `gdal` manually, therefore for using georeferencer, installation 
with conda is recommended.

### Install with `conda`

To install package with conda you should install anaconda or miniconda first.
See installation: https://docs.conda.io/en/latest/miniconda.html.

When conda is installed, clone the repository and create conda environment from `environment.yml` file.

```
git clone https://github.com/aerospaceresearch/DirectDemod
cd DirectDemod/
conda env create -f environment.yml -n env_name
conda activate env_name
```

You should add `directdemod` package to your `PYTHONPATH`. 
<br>
On Windows edit environment variable `PYTHONPATH` and append path to DirectDemod directory to it.
On Linux edit `.bashrc`.

```
export PYTHONPATH=$PYTHONPATH:/path/to/DirectDemod
```

Update `.bashrc`.

```
source ~/.bashrc
```

### Install with pip

To install with pip, fist clone repository, then install requirements with `pip` 

```
git clone https://github.com/aerospaceresearch/DirectDemod
cd DirectDemod/
pip install -r requirements.txt
```

You should add `directdemod` package to your `PYTHONPATH`. 
<br>
On Windows edit environment variable `PYTHONPATH` and append path to DirectDemod directory to it.
On Linux edit `.bashrc`.

```
export PYTHONPATH=$PYTHONPATH:/path/to/DirectDemod
```

Update `.bashrc`.

```
source ~/.bashrc
```

For installation of `gdal` please refer to 

- https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html.

### Test installation

To test installation, run the following command. You should see message, that 
tests were passed successfully.

**Note:** in case you haven't installed `gdal` part of the tests will result in errors.

```
pytest
```

## Documentation
Please find the docs at: [directdemod.readthedocs.io](https://directdemod.readthedocs.io)

## Experiments
The experiments performed to make design decisions are in the folder experiments, as jupyter notebooks. (click the binder badge for an online version)

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/aerospaceresearch/DirectDemod/Vinay_dev)[![Documentation Status](https://readthedocs.org/projects/directdemod/badge/?version=vinay_dev)](http://directdemod.readthedocs.io/en/vinay_dev/?badge=vinay_dev)
