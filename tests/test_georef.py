import os
import unittest

from PIL import Image
from directdemod.misc import save_metadata
from directdemod.georeferencer import Georeferencer


class TestGeoref(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.sdr = 'tests/data/georef/SDRSharp_20190521_170204Z_137500000Hz_IQ.wav'
        self.image = 'tests/data/georef/start.png'
        self.tle = 'tle/noaa18_June_14_2018.txt'

        self.f  = 'tests/data/georef/start.tif'
        self.result = 'tests/data/georef/result.tif'

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.f):
            os.remove(self.f)

    def test_georef_tif(self):
        g = Georeferencer(self.tle)

        save_metadata(self.sdr, self.image, 'NOAA 19', self.tle)

        g.georef_tif(self.f, self.f)  # georef self.f and save to self.f

        img = Image.open(self.result)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
