import os
import unittest
import contextlib

from PIL import Image
from shutil import copyfile
from directdemod.georeferencer import Georeferencer

class TestGeoref(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.start  = 'tests/data/georef/start.tif'
        self.result = 'tests/data/georef/result.tif'
        self.tle    = 'tle/noaa18_June_14_2018.txt'
        self.f      = 'tests/data/georef/_sample.tif'

        copyfile(self.start, self.f)

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.f):
            os.remove(self.f)

    def test_georef_tif(self):
        g = Georeferencer(self.tle)

        with contextlib.redirect_stderr(None):
            with contextlib.redirect_stdout(None):
                g.georef_tif(self.f, self.f) # georef self.f and save to self.f

        img = Image.open(self.result)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
