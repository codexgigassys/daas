""" Test whether the construction of decompilers is done correctly or not. """
from ..decompiler_factory import DecompilerFactory
from ..decompiler import SubprocessBasedDecompiler

import unittest


class TestDecompilerWithMinimalArguments(unittest.TestCase):
    def setUp(self) -> None:
        self.decompiler = DecompilerFactory().create(config={'decompiler_name': 'Just Decompiler',
                                                             'sample_type': 'pe',
                                                             'extension': 'exe',
                                                             'version': 4,
                                                             'source_compression_algorithm': 'xztar',
                                                             'requires_library': False,
                                                             'decompiler_command': 'some command'})

    def test_decompiler_name(self):
        self.assertEqual(self.decompiler.decompiler_name, 'Just Decompiler')

    def test_file_type(self):
        self.assertEqual(self.decompiler.file_type, 'pe')

    def test_extension(self):
        self.assertEqual(self.decompiler.extension, 'exe')

    def test_version(self):
        self.assertEqual(self.decompiler.version, 4)

    def test_source_compression_algorithm(self):
        self.assertEqual(self.decompiler.source_compression_algorithm, 'xztar')

    def test_class(self):
        self.assertIsInstance(self.decompiler, SubprocessBasedDecompiler)

    def test_nice(self):
        self.assertEqual(self.decompiler.nice, 0)

    def test_timeout(self):
        self.assertEqual(self.decompiler.timeout, 120)

    def test_creates_windows(self):
        self.assertFalse(self.decompiler.creates_windows)

    def test_processes_to_kill(self):
        self.assertListEqual(self.decompiler.processes_to_kill, [])

    def test_custom_current_working_directory(self):
        self.assertEqual(self.decompiler.custom_current_working_directory, None)

    def test_decompiler_command(self):
        self.assertEqual(self.decompiler.decompiler_command, 'some command')


class TestDecompilerWithAllPossibleArguments(unittest.TestCase):
    def setUp(self) -> None:
        self.decompiler_command = "do something @sample_path '-value 10' '-output @extraction_path'"
        self.decompiler = DecompilerFactory().create(config={'decompiler_name': 'random decompiler',
                                                             'sample_type': 'java',
                                                             'extension': 'jar',
                                                             'version': 2,
                                                             'source_compression_algorithm': 'xztar',
                                                             'requires_library': False,
                                                             'nice': 3,
                                                             'timeout': 111,
                                                             'creates_windows': True,
                                                             'processes_to_kill': ['*something'],
                                                             'custom_current_working_directory': '/cwd',
                                                             'decompiler_command': self.decompiler_command})

    def test_decompiler_name(self):
        self.assertEqual(self.decompiler.decompiler_name, 'random decompiler')

    def test_file_type(self):
        self.assertEqual(self.decompiler.file_type, 'java')

    def test_extension(self):
        self.assertEqual(self.decompiler.extension, 'jar')

    def test_version(self):
        self.assertEqual(self.decompiler.version, 2)

    def test_source_compression_algorithm(self):
        self.assertEqual(self.decompiler.source_compression_algorithm, 'xztar')

    def test_class(self):
        self.assertIsInstance(self.decompiler, SubprocessBasedDecompiler)

    def test_nice(self):
        self.assertEqual(self.decompiler.nice, 3)

    def test_timeout(self):
        self.assertEqual(self.decompiler.timeout, 111)

    def test_creates_windows(self):
        self.assertTrue(self.decompiler.creates_windows)

    def test_processes_to_kill(self):
        self.assertListEqual(self.decompiler.processes_to_kill, ['*something'])

    def test_custom_current_working_directory(self):
        self.assertEqual(self.decompiler.custom_current_working_directory, '/cwd')

    def test_decompiler_command(self):
        self.assertEqual(self.decompiler.decompiler_command, self.decompiler_command)
