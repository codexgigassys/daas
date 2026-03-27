import unittest

from ..redis.task import Task
from ..gridfs import storage


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


class TaskWithStorageFileIDTest(unittest.TestCase):
    def setUp(self) -> None:
        self.storage_file_id = storage.upload_file(stream=b'aaaaa', name='7zip')
        self.task = Task({'force_reprocess': False,
                          'storage_file_id': self.storage_file_id,
                          'api_url': 'https://api.url/placeholder/',
                          'file_name': '7zip',
                          'uploaded_on': '2019-12-15'})

    def tearDown(self) -> None:
        storage.delete_file(self.storage_file_id)

    def test_sample_sha1(self):
        self.assertEqual(self.task.sample.sha1, 'df51e37c269aa94d38f93e537bf6e2020b21406c')

    def test_sample_size(self):
        self.assertEqual(self.task.sample.size, 5)
