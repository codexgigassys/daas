import unittest

from ..sample import Sample
from ..seaweed import seaweedfs


class SampleTestSuite(unittest.TestCase):
    def setUp(self) -> None:
        with open(self.file_path, 'rb') as file:
            content = file.read()
            file_name = 'file name'
            seaweedfs_file_id = seaweedfs.upload_file(stream=content, name=file_name)
            self.sample = Sample(file_name=file_name, content=content, password=b'', uploaded_on='2019-12-14',
                                 seaweedfs_file_id=seaweedfs_file_id)

    def tearDown(self) -> None:
        self.sample.delete_from_seaweedfs()


class TestSample(SampleTestSuite):
    file_path = '/daas/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'

    def test_sample_size(self):
        self.assertEqual(self.sample.size, 532480)

    def test_sample_md5(self):
        self.assertEqual(self.sample.md5, '460f0c273d1dc133ed7ac1e24049ac30')

    def test_sample_sha1(self):
        self.assertEqual(self.sample.sha1, '5f31f795047da2d478b69ca27b8c7ed2df14b70a')

    def test_sample_sha2(self):
        self.assertEqual(self.sample.sha2, '36c50c6a795035f1bfa7735fd1cd82d59926716405a79f9abca4253c65c76638')

    def test_sample_file_type(self):
        self.assertEqual(self.sample.file_type, 'pe')

    def test_sample_file_type(self):
        self.assertEqual(self.sample.metadata, {'size': 532480,
                                                'md5': '460f0c273d1dc133ed7ac1e24049ac30',
                                                'sha1': '5f31f795047da2d478b69ca27b8c7ed2df14b70a',
                                                'sha2': '36c50c6a795035f1bfa7735fd1cd82d59926716405a79f9abca4253c65c76638',
                                                'file_type': 'pe',
                                                'seaweedfs_file_id': self.sample.seaweedfs_file_id,
                                                'uploaded_on': '2019-12-14',
                                                'subfiles': []})
    
    def test_sample_is_valid(self):
        self.assertTrue(self.sample.file_type)


class TestZipSample(SampleTestSuite):
    file_path = '/daas/tests/resources/zip.zip'

    def test_sample_file_type(self):
        self.assertEqual(self.sample.file_type, 'zip')

    def test_number_of_subfiles(self):
        self.assertEqual(len(self.sample.subfiles), 2)

    def test_first_subfile_sha1(self):
        self.assertEqual(self.sample.subfiles[0].sha1, '5f31f795047da2d478b69ca27b8c7ed2df14b70a')
