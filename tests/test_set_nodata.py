import os
import gdal
import unittest

from PIL import Image
from shutil import copyfile
from directdemod.georeferencer import set_nodata

class TestSetNoData(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.nodata = 0
        self.nodata255 = os.path.abspath('tests/data/no_data/nodata255.tif')
        self.nodata0   = os.path.abspath('tests/data/no_data/nodata0.tif')
        self.f         = os.path.abspath('tests/data/no_data/_sample.tif')

        copyfile(self.nodata255, self.f)

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.f):
            os.remove(self.f)

    def test_set_nodata(self):
        set_nodata(self.nodata255, self.f, value = self.nodata)

        img = Image.open(self.nodata0)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)

        data = gdal.Open(self.f)
        self.assertEqual(data.GetRasterBand(1).GetNoDataValue(), self.nodata)
