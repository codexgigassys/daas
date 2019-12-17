import unittest

from ..classifier import get_identifier_of_file


class TestClassifier(unittest.TestCase):
    def _classify_file(self, file_name) -> str:
        with open(f'/daas/tests/resources/{file_name}', 'rb') as file:
            return get_identifier_of_file(file.read())

    def test_classify_pe(self):
        self.assertEqual(self._classify_file('460f0c273d1dc133ed7ac1e24049ac30.csharp'), 'pe')

    def test_classify_flash(self):
        self.assertEqual(self._classify_file('eb19009c086845d0408c52d495187380c5762b8c.flash'), 'flash')

    def test_classify_java(self):
        self.assertEqual(self._classify_file('144e0f0befb2509b3004b6c9f4fab57cdd16279b.codex'), 'java')

    def test_classify_zip(self):
        self.assertEqual(self._classify_file('zip.zip'), 'zip')

    def test_classify_unknown(self):
        self.assertEqual(self._classify_file('text.txt'), None)
