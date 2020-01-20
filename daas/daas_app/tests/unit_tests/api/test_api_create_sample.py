from ...test_utils.test_cases.generic import APITestCase
from ....models import Sample, Result
from ....utils.task_manager import TaskManager
from ...test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02
from ....utils.callback_manager import CallbackManager
from ....utils.status.sample import SampleStatus


SERIALIZED_SAMPLE = {'size': 155,
                     'md5': 'a'*32,
                     'sha1': 'b'*40,
                     'sha2': 'c'*64,
                     'file_type': 'flash',
                     'seaweedfs_file_id': '3,01637037d6',
                     'uploaded_on': '2020-01-15',
                     'file_name': 'flash_sample.swf',
                     'subfiles': []}

SERIALIZED_JAVA_SAMPLE = {'size': 123,
                          'md5': '1'*32,
                          'sha1': '2'*40,
                          'sha2': '3'*64,
                          'file_type': 'java',
                          'seaweedfs_file_id': '2,11637037e1',
                          'uploaded_on': '2020-01-15',
                          'file_name': 'another_sample.jar',
                          'subfiles': []}

SERIALIZED_ZIP_SAMPLE = {'size': 522,
                         'md5': 'd'*32,
                         'sha1': 'e'*40,
                         'sha2': 'f'*64,
                         'file_type': 'zip',
                         'seaweedfs_file_id': None,
                         'uploaded_on': '2020-01-15',
                         'file_name': 'zipped_file.zip',
                         'subfiles': [SERIALIZED_SAMPLE, SERIALIZED_JAVA_SAMPLE]}


class CreateSampleAPITest(APITestCase):
    def setUp(self):
        TaskManager().__mock__()  # to avoid uploading samples for real
        self.serialized_sample = SERIALIZED_SAMPLE
        self.serialized_zip_sample = SERIALIZED_ZIP_SAMPLE
        self.create_sample_url = '/internal/api/create_sample/'
        TaskManager().__mock__()  # to reset submit sample calls to zero
        #CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of TaskManager

    def test_serialize_single_sample(self):
        data = {'sample': self.serialized_sample}
        response = self.client.post(self.create_sample_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['non_zip_samples'], 1)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_serialize_zip_sample(self):
        data = {'sample': self.serialized_zip_sample}
        response = self.client.post(self.create_sample_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['non_zip_samples'], 2)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 2)
