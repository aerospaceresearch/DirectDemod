import os
import unittest

from PIL import Image
from directdemod.merger import merge
from directdemod import constants


class TestMerge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.average = constants.MODULE_PATH + '/tests/data/merge/average.tif'
        cls.max = constants.MODULE_PATH + '/tests/data/merge/max.tif'
        cls.first = constants.MODULE_PATH + '/tests/data/merge/first.tif'
        cls.last = constants.MODULE_PATH + '/tests/data/merge/last.tif'

        cls.files = [constants.MODULE_PATH + '/tests/data/merge/image1.tif',
                     constants.MODULE_PATH + '/tests/data/merge/image2.tif']

        cls.saverage = constants.MODULE_PATH + '/tests/data/merge/saverage.tif'
        cls.smax = constants.MODULE_PATH + '/tests/data/merge/smax.tif'
        cls.sfirst = constants.MODULE_PATH + '/tests/data/merge/sfirst.tif'
        cls.slast = constants.MODULE_PATH + '/tests/data/merge/slast.tif'

    @classmethod
    def tearDownClass(cls):
        images = [cls.saverage, cls.smax, cls.sfirst, cls.slast]

        for image in images:
            if os.path.isfile(image):
                os.remove(image)

    def assertImages(self, image_path1, image_path2):
        im1 = Image.open(image_path1)
        im2 = Image.open(image_path2)

        self.assertEqual(im1, im2)

    def test_average(self):
        merge(self.files, self.saverage, "average")
        self.assertImages(self.average, self.saverage)

    def test_max(self):
        merge(self.files, self.smax, "max")
        self.assertImages(self.max, self.smax)

    def test_first(self):
        merge(self.files, self.sfirst, "first")
        self.assertImages(self.first, self.sfirst)

    def test_last(self):
        merge(self.files, self.slast, "last")
        self.assertImages(self.last, self.slast)
