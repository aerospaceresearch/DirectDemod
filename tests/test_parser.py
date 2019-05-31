import os
import json
import unittest

from directdemod.misc import JSON, Encoder

class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.path = os.path.abspath('tests/data/parser/parser.json')
        self.dict = json.load(open(self.path, 'r'))
        self.string = json.dumps(json.load(open(self.path, 'r')), cls=Encoder)
        self.ofile = os.path.abspath('tests/data/parser/_sample.json')

    @classmethod
    def tearDownClass(self):
        if os.path.isfile(self.ofile):
            os.remove(self.ofile)

    def test_parse(self):
        d = JSON.parse(self.string)

        self.assertEqual(d, self.dict)
        self.assertEqual(d["image_name"], self.dict["image_name"])
        self.assertEqual(d["sat_type"],   self.dict["sat_type"])
        self.assertEqual(d["date_time"],  self.dict["date_time"])
        self.assertEqual(d["center"],     self.dict["center"])
        self.assertEqual(d["direction"],  self.dict["direction"])

    def test_stringify(self):
        self.assertEqual(JSON.stringify(self.dict), self.string)

    def test_from_file(self):
        d = JSON.from_file(self.path)

        self.assertEqual(d, self.dict)
        self.assertEqual(d["image_name"], self.dict["image_name"])
        self.assertEqual(d["sat_type"],   self.dict["sat_type"])
        self.assertEqual(d["date_time"],  self.dict["date_time"])
        self.assertEqual(d["center"],     self.dict["center"])
        self.assertEqual(d["direction"],  self.dict["direction"])

    def test_save(self):
        JSON.save(self.dict, self.ofile)

        self.assertTrue(os.path.isfile(self.ofile))
        text = open(self.path, 'r').read().strip()
        self.assertEqual(text, self.string)
