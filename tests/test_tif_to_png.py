import os
import unittest

from PIL import Image
from directdemod.georeferencer import tif_to_png


class TestConvert(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tif = os.path.abspath('tests/data/tif_to_png/sample.tif')
        cls.png = os.path.abspath('tests/data/tif_to_png/sample.png')
        cls.f = os.path.abspath('tests/data/tif_to_png/_sample.png')

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.f):
            os.remove(cls.f)

    def test_tif_to_png(self):
        tif_to_png(self.tif, self.f)

        img = Image.open(self.png)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)
        self.assertRaises(NotImplementedError, tif_to_png, '', '', False)
