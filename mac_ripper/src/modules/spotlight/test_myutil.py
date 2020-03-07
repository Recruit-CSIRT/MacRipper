# -*- coding: utf-8 -*-
import unittest
from modules.spotlight.myutil import *


class TestMyUtil(unittest.TestCase):
    def test_add_timezone_difference(self):
        cases = [
            {"arg": "2020-05-22 15:00:00 +0000", "timezone": "asia/tokyo", "expected": "2020-05-23 00:00:00"},
            {"arg": "2020-05-22 15:00:00 +0000", "timezone": "America/New_York", "expected": "2020-05-22 11:00:00"},
        ]
        input_format = "%Y-%m-%d %H:%M:%S %z"
        output_format = "%Y-%m-%d %H:%M:%S"
        for c in cases:
            t = timedelta(c["arg"], input_format, output_format, c["timezone"])
            self.assertEqual(t, c["expected"])

    def test_double_quote(self):
        self.assertEqual(double_quote("hello"), '"hello"')


if __name__ == "__main__":
    unittest.main()
