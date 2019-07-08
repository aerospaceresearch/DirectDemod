import os
import unittest

from osgeo import gdal
from PIL import Image
from shutil import copyfile
from directdemod import constants
from directdemod.georeferencer import _set_nodata


class TestSetNoData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nodata = 0
        cls.nodata255 = constants.MODULE_PATH + '/tests/data/no_data/nodata255.tif'
        cls.nodata0 = constants.MODULE_PATH + '/tests/data/no_data/nodata0.tif'
        cls.f = constants.MODULE_PATH + '/tests/data/no_data/_sample.tif'

        copyfile(cls.nodata255, cls.f)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.f):
            os.remove(cls.f)

    def test_set_nodata(self):
        _set_nodata(self.nodata255, self.f, value=self.nodata)

        img = Image.open(self.nodata0)
        img_new = Image.open(self.f)

        self.assertEqual(img, img_new)

        data = gdal.Open(self.f)
        self.assertEqual(data.GetRasterBand(1).GetNoDataValue(), self.nodata)
