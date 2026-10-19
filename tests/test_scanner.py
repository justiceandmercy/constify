"""Tests for scanner and reporter."""

import os
import tempfile
import unittest

from scanner import extract_strings, scan_directory
from reporter import format_text, format_json


class TestExtractStrings(unittest.TestCase):
    def test_basic(self):
        src = 'x = "hello"\ny = \'world\'\n'
        got = extract_strings(src)
        values = [v for v, _ in got]
        self.assertIn("hello", values)
        self.assertIn("world", values)

    def test_comment_stripped(self):
        src = '# "ignored"\nvalue = "kept"\n'
        got = extract_strings(src)
        values = [v for v, _ in got]
        self.assertNotIn("ignored", values)
        self.assertIn("kept", values)

    def test_line_numbers(self):
        src = 'a = "first"\n' * 0 + 'x="one"\n' + 'y="two"\n'
        got = extract_strings("x=\"one\"\ny=\"two\"\n")
        self.assertEqual(got[0][1], 1)
        self.assertEqual(got[1][1], 2)


class TestScanDirectory(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "sub"))
        with open(os.path.join(self.d, "a.py"), "w") as f:
            f.write('MSG = "repeated string here"\nprint("repeated string here")\nprint("repeated string here")\n')
        with open(os.path.join(self.d, "sub", "b.js"), "w") as f:
            f.write('const x = "repeated string here";\n')
        with open(os.path.join(self.d, "c.py"), "w") as f:
            f.write('print("short")\n')

    def test_finds_repeated(self):
        res = scan_directory(self.d, min_count=3, min_length=4)
        self.assertIn("repeated string here", res.counts)
        self.assertEqual(res.counts["repeated string here"], 4)

    def test_filters_short(self):
        res = scan_directory(self.d, min_count=1, min_length=10)
        self.assertNotIn("short", res.counts)

    def test_exclude(self):
        res = scan_directory(self.d, min_count=3, min_length=4, exclude={"sub"})
        # still 3 occurrences in a.py
        self.assertEqual(res.counts.get("repeated string here"), 3)

    def test_format_text(self):
        res = scan_directory(self.d, min_count=3, min_length=4)
        out = format_text(res)
        self.assertIn("repeated string here", out)

    def test_format_json(self):
        res = scan_directory(self.d, min_count=3, min_length=4)
        out = format_json(res)
        self.assertIn('"string"', out)


if __name__ == "__main__":
    unittest.main()
