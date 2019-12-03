import unittest
import hashlib

from ..get_sample import get_sample


class TestGetSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = get_sample('https://www.7-zip.org/a/7z1900-x64.exe')

    def test_content_size(self):
        self.assertEqual(len(self.content), 1447178)

    def test_content_hash(self):
        self.assertEqual(hashlib.sha1(self.content).hexdigest(), '9fa11a63b43f83980e0b48dc9ba2cb59d545a4e8')
