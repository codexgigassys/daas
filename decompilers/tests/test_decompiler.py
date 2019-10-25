from ..decompiler_factory import DecompilerFactory
from ..decompiler import SubprocessBasedDecompiler

import unittest


class TestDecompiler(unittest.TestCase):
    def setUp(self) -> None:
        self.decompiler_command = "decompile @sample_path '-output @extraction_path' -value 10"
        self.decompiler = SubprocessBasedDecompiler(decompiler_name='Just decompiler',
                                                    file_type='pe',
                                                    extension='exe',
                                                    source_compression_algorithm='xztar',
                                                    nice=3,
                                                    timeout=100,
                                                    creates_windows=False,
                                                    decompiler_command=self.decompiler_command,
                                                    processes_to_kill=[r'*something'],
                                                    custom_current_working_directory='/cwd',
                                                    version=7)

    def test_requires_nice(self):
        self.assertTrue(self.decompiler.requires_nice)

    def test_requires_timeout(self):
        self.assertTrue(self.decompiler.requires_timeout)

    def test_get_current_working_directory(self):
        self.assertEqual(self.decompiler.get_current_working_directory(), '/cwd')

    def test_nice_command_arguments(self):
        self.assertListEqual(self.decompiler.nice_command_arguments(), ['nice', '-n', '3'])

    def test_timeout_command_arguments(self):
        self.assertListEqual(self.decompiler.timeout_command_arguments(), ['timeout', '-k', '30', '100'])

    def test_xvfb_command_arguments(self):
        self.assertListEqual(self.decompiler.xvfb_command_arguments(), ['xvfb-run'])

    def test_replace_paths(self):
        self.assertEqual(self.decompiler.replace_paths(self.decompiler_command),
                         "decompile /tmpfs/pe.exe '-output /tmpfs/pe' -value 10")

    def test_split_command(self):
        self.assertEqual(self.decompiler.split_command(),
                         ['decompile', '@sample_path', '-output @extraction_path', '-value', '10'])

    def test_full_command(self):
        self.assertListEqual(self.decompiler.full_command(),
                             ['nice', '-n', '3', 'timeout', '-k', '30', '100'] +
                             ['decompile', '/tmpfs/pe.exe', '-output /tmpfs/pe', '-value', '10'])
