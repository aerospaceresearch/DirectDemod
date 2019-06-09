import os
import json
import unittest

from directdemod.misc import JSON, Encoder
from directdemod import constants


class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path = constants.MODULE_PATH + '/tests/data/parser/parser.json'
        cls.dict = json.load(open(cls.path, 'r'))
        cls.string = json.dumps(json.load(open(cls.path, 'r')), cls=Encoder)
        cls.ofile = constants.MODULE_PATH + '/tests/data/parser/_sample.json'

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.ofile):
            os.remove(cls.ofile)

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
