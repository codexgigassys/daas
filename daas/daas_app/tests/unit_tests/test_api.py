from ..test_utils.test_cases.generic import APITestCase, NonTransactionalLiveServerTestCase
from ...models import Sample, Result
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02
from ...utils.callback_manager import CallbackManager
from ...utils.status.sample import SampleStatus


class GetSamplesFromHashTest(APITestCase):
    def setUp(self):
        TaskManager().__mock__()
        self.serialized_sample = {'size': 155,
                                  'md5': 'a'*32,
                                  'sha1': 'b'*40,
                                  'sha2': 'c'*64,
                                  'file_type': 'flash',
                                  'seaweedfs_file_id': '3,01637037d6',
                                  'uploaded_on': '2020-01-15',
                                  'file_name': 'flash_sample.swf'}

    def test_no_samples(self):
        response = self.client.get(f'/api/get_sample_from_hash/{"0"*40}', format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_one_sample_using_md5(self):
        Sample.objects.create(**self.serialized_sample)
        md5 = self.serialized_sample['md5']
        response = self.client.get(f'/api/get_sample_from_hash/{md5}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('md5'), md5)

    def test_get_one_sample_using_sha1(self):
        Sample.objects.create(**self.serialized_sample)
        sha1 = self.serialized_sample['sha1']
        response = self.client.get(f'/api/get_sample_from_hash/{sha1}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha1'), sha1)

    def test_get_one_sample_using_sha2(self):
        Sample.objects.create(**self.serialized_sample)
        sha2 = self.serialized_sample['sha2']
        response = self.client.get(f'/api/get_sample_from_hash/{sha2}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha2'), sha2)


class UploadAPITest(NonTransactionalLiveServerTestCase):
    def setUp(self):
        TaskManager().__mock__()
        Sample.objects.all().delete()  # Wipe samples created by meta_extractor.

    def test_upload_a_sample(self):
        self.upload_file(CSHARP_SAMPLE)
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(Sample.objects.all()[0].file_name, '460f0c273d1dc133ed7ac1e24049ac30.csharp')

    def test_upload_two_samples(self):
        self.upload_file(CSHARP_SAMPLE)
        self.upload_file(FLASH_SAMPLE_01)
        self.wait_sample_creation(2)
        self.assertEqual(Sample.objects.count(), 2)

    def test_file_type_correctly_detected(self):
        self.upload_file(FLASH_SAMPLE_01)
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')

    def test_file_content_not_modified(self):
        self.upload_file(FLASH_SAMPLE_02)
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.all()[0].sha1, 'eb19009c086845d0408c52d495187380c5762b8c')

    def test_upload_url(self):
        self.upload_file(file_url='https://www.7-zip.org/a/7z1900.exe',
                         file_name='ilspy')
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.all()[0].sha1, '2f23a6389470db5d0dd2095d64939657d8d3ea9d')


class ReprocessAPITest(NonTransactionalLiveServerTestCase):
    def setUp(self):
        Sample.status = SampleStatus.DONE  # to make the test more unitary. Otherwise we would need to create fake tasks and results.
        TaskManager().__mock__()  # to avoid uploading samples for real
        Sample.objects.all().delete()  # Wipe samples created by meta_extractor.
        Result.objects.all().delete()  # Wipe samples created by meta_extractor.
        self.serialized_sample = {'size': 155,
                                  'md5': 'a'*32,
                                  'sha1': 'b'*40,
                                  'sha2': 'c'*64,
                                  'file_type': 'flash',
                                  'seaweedfs_file_id': '3,01637037d6',
                                  'uploaded_on': '2020-01-15',
                                  'file_name': 'flash_sample.swf'}
        self.sample = Sample.objects.create(**self.serialized_sample)
        self.serialized_result = {'status': 1,
                                  'output': '',
                                  'decompiler': 'decompiler',
                                  'sample': self.sample,
                                  'extension': 'exe'}
        Result.objects.create(**self.serialized_result)
        TaskManager().__mock__()  # to reset submit sample calls to zero
        CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of TaskManager

    def test_nothing_to_reprocess(self):
        data = {'hashes': [self.sample.md5]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 0)

    def test_reprocess_with_md5(self):
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.md5]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_reprocess_with_sha1(self):
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.sha1]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_reprocess_with_sha2(self):
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.sha2]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_force_reprocess(self):
        data = {'hashes': [self.sample.md5], 'force_reprocess': True}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)
