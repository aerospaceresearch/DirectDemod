import os
import unittest

from PIL import Image
from shutil import copyfile
from directdemod import constants
from directdemod.georeferencer import overlay


class TestOverlay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.borders   = constants.MODULE_PATH + '/tests/data/overlay/shapes/borders.shp'
        cls.with_over = constants.MODULE_PATH + '/tests/data/overlay/with_overlay.tif'
        cls.no_over   = constants.MODULE_PATH + '/tests/data/overlay/no_overlay.tif'
        cls.f         = constants.MODULE_PATH + '/tests/data/overlay/_sample.tif'

        copyfile(cls.no_over, cls.f)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.f):
            os.remove(cls.f)

    def test_overlay(self):
        overlay(self.f, shapefile=self.borders)

        img = Image.open(self.with_over)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
