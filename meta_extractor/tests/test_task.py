import unittest

from ..redis.task import Task
from ..seaweed import seaweedfs


class TaskWithExternalURLTest(unittest.TestCase):
    def setUp(self) -> None:
        self.task = Task({'force_reprocess': False,
                          'external_url': 'https://www.7-zip.org/a/7z1900.exe',
                          'api_url': 'https://api.url/placeholder/',
                          'file_name': '7zip',
                          'uploaded_on': '2019-12-15'})

    def test_sample_sha1(self):
        self.assertEqual(self.task.sample.sha1, '2f23a6389470db5d0dd2095d64939657d8d3ea9d')

    def test_sample_size(self):
        self.assertEqual(self.task.sample.size, 1185968)


class TaskWithSeaweedfsFileIDTest(unittest.TestCase):
    def setUp(self) -> None:
        self.seaweedfs_file_id = seaweedfs.upload_file(stream=b'aaaaa', name='7zip')
        self.task = Task({'force_reprocess': False,
                          'seaweedfs_file_id': self.seaweedfs_file_id,
                          'api_url': 'https://api.url/placeholder/',
                          'file_name': '7zip',
                          'uploaded_on': '2019-12-15'})

    def tearDown(self) -> None:
        seaweedfs.delete_file(self.seaweedfs_file_id)

    def test_sample_sha1(self):
        self.assertEqual(self.task.sample.sha1, 'df51e37c269aa94d38f93e537bf6e2020b21406c')

    def test_sample_size(self):
        self.assertEqual(self.task.sample.size, 5)
