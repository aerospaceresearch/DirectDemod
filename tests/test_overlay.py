import os
import unittest

from PIL import Image
from shutil import copyfile
from directdemod.georeferencer import overlay

class TestOverlay(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.borders = os.path.abspath('tests/data/overlay/shapes/borders.shp')
        self.with_over = os.path.abspath('tests/data/overlay/with_overlay.tif')
        self.no_over = os.path.abspath('tests/data/overlay/no_overlay.tif')
        self.f = os.path.abspath('tests/data/overlay/_sample.tif')

        copyfile(self.no_over, self.f)

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.f):
            os.remove(self.f)

    def test_overlay(self):
        overlay(self.f, shapefile=self.borders)

        img = Image.open(self.with_over)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
