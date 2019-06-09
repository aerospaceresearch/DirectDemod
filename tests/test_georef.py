import os
import unittest

from PIL import Image
from directdemod import constants
from directdemod.misc import save_metadata
from directdemod.georeferencer import Georeferencer


class TestGeoref(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sdr = constants.MODULE_PATH + '/tests/data/georef/SDRSharp_20190521_170204Z_137500000Hz_IQ.wav'
        cls.image = constants.MODULE_PATH + '/tests/data/georef/start.png'
        cls.tle = constants.MODULE_PATH + '/tle/noaa18_June_14_2018.txt'

        cls.f  = constants.MODULE_PATH + '/tests/data/georef/start.tif'
        cls.result = constants.MODULE_PATH + '/tests/data/georef/result.tif'

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.f):
            os.remove(cls.f)

    def test_georef_tif(self):
        g = Georeferencer(self.tle)

        save_metadata(self.sdr, self.image, 'NOAA 19', self.tle)

        g.georef_tif(self.f, self.f)  # georef self.f and save to self.f

        img = Image.open(self.result)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
