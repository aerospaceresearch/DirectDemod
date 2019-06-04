import unittest

from datetime import datetime
from directdemod.misc import extract_date, to_datetime


class TestExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.f1 = 'SDRSharp_20180615_140752Z_137120000Hz_IQ'
        cls.f2 = 'SDRSharp_20190521_152538Z_137500000Hz_IQ'
        cls.f3 = 'SDRSharp_20190521_165349Z_137500000Hz_IQ'

        cls.d1 = datetime(2018, 6, 15, 14, 7, 52)
        cls.d2 = datetime(2019, 5, 21, 15, 25, 38)
        cls.d3 = datetime(2019, 5, 21, 16, 53, 49)

    def test_extract_date(cls):
        d1 = extract_date(cls.f1)
        d2 = extract_date(cls.f2)
        d3 = extract_date(cls.f3)

        cls.assertEqual(d1, cls.d1)
        cls.assertEqual(d2, cls.d2)
        cls.assertEqual(d3, cls.d3)

        cls.assertRaises(ValueError, extract_date, 'SDRSharp')
        cls.assertRaises(ValueError, extract_date, 'SDRSharp_20190521_165349_137500000Hz_IQ')

    def test_to_datetime(self):
        d1 = to_datetime(self.f1[18:24], self.f1[9:17])
        d2 = to_datetime(self.f2[18:24], self.f2[9:17])
        d3 = to_datetime(self.f3[18:24], self.f3[9:17])

        self.assertEqual(d1, self.d1)
        self.assertEqual(d2, self.d2)
        self.assertEqual(d3, self.d3)

        self.assertRaises(ValueError, to_datetime, 'text', 'text')
        self.assertRaises(ValueError, to_datetime, '165349text', '20190521text')
