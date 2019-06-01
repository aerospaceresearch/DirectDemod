import os
import tifffile
import unittest

from directdemod.misc import JSON


class TestSaveMeta(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.data = {
            'image_name': 'samples/image_noaa_2.png',
            'sat_type': 'NOAA 19',
            'date_time': '2019-05-21T15:25:38',
            'center': [61.49394255712926, 2.69093612636276],
            'direction': 203.91859857008012
        }

        self.path = os.path.abspath('tests/data/metadata/example.tif')

    def test_save(self):
        with tifffile.TiffFile(self.path) as f:
            page = f.pages[0]
            descriptor = page.tags["ImageDescription"].value

        descriptor = JSON.parse(descriptor)

        self.assertEqual(self.data, descriptor)
