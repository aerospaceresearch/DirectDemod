import os
import unittest

from PIL import Image
from directdemod.georeferencer import tif_to_png

class TestConvert(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tif = os.path.abspath('tests/data/tif_to_png/sample.tif')
        self.png = os.path.abspath('tests/data/tif_to_png/sample.png')
        self.f = os.path.abspath('tests/data/tif_to_png/_sample.png')

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.f):
            os.remove(self.f)

    def test_tif_to_png(self):
        tif_to_png(self.tif, self.f)

        img = Image.open(self.png)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
        self.assertRaises(NotImplementedError, tif_to_png, '', '', False)
