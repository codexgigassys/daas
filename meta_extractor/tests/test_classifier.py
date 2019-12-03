import unittest

from ..process import process


class TestProcess(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open('/daas/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp', 'rb') as file:
            cls.metadata = process(file.read())

    def test_size(self):
        self.assertEqual(self.metadata['size'], 532480)

    def test_md5(self):
        self.assertEqual(self.metadata['md5'], '460f0c273d1dc133ed7ac1e24049ac30')

    def test_sha1(self):
        self.assertEqual(self.metadata['sha1'], '5f31f795047da2d478b69ca27b8c7ed2df14b70a')

    def test_sha2(self):
        self.assertEqual(self.metadata['sha2'], '36c50c6a795035f1bfa7735fd1cd82d59926716405a79f9abca4253c65c76638')

    def test_file_type(self):
        self.assertEqual(self.metadata['file_type'], 'pe')
