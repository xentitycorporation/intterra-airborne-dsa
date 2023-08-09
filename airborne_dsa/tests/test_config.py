import unittest
import os
from jsonschema import ValidationError
from ..config import Config


class TestConfig(unittest.TestCase):
    def test_bad_schema(self):
        root_directory = os.path.dirname(os.path.realpath(__file__))
        with self.assertRaises(ValidationError):
            Config.load_config(root_directory + "/bad_config.json")

    def test_good_schema(self):
        root_directory = os.path.dirname(os.path.realpath(__file__))
        config = Config.load_config(root_directory + "/good_config.json")
        self.assertEqual(config["bucket"], "hi")
