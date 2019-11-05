from ..test_utils.test_cases.generic import APITestCase
from ...models import Sample, Result
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02
from ...utils.callback_manager import CallbackManager


class GetSamplesFromHashTest(APITestCase):
    def setUp(self):
        TaskManager().__mock__()

    def test_no_samples(self):
        response = self.client.get(f'/api/get_sample_from_hash/{"0"*40}', format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_one_sample_using_md5(self):
        self.upload_file(CSHARP_SAMPLE)
        md5 = Sample.objects.all()[0].md5
        response = self.client.get(f'/api/get_sample_from_hash/{md5}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("md5"), md5)

    def test_get_one_sample_using_sha1(self):
        self.upload_file(CSHARP_SAMPLE)
        sha1 = Sample.objects.all()[0].sha1
        md5 = Sample.objects.all()[0].md5
        response = self.client.get(f'/api/get_sample_from_hash/{sha1}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("md5"), md5)

    def test_get_one_sample_using_sha2(self):
        self.upload_file(CSHARP_SAMPLE)
        sha2 = Sample.objects.all()[0].sha2
        md5 = Sample.objects.all()[0].md5
        response = self.client.get(f'/api/get_sample_from_hash/{sha2}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("md5"), md5)


class UploadAPITest(APITestCase):
    def test_upload_a_sample(self):
        self.upload_file(CSHARP_SAMPLE)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(Sample.objects.all()[0].name, '460f0c273d1dc133ed7ac1e24049ac30.csharp')

    def test_upload_two_samples(self):
        self.upload_file(CSHARP_SAMPLE)
        self.upload_file(FLASH_SAMPLE_01)
        self.assertEqual(Sample.objects.count(), 2)

    def test_file_type_correctly_detected(self):
        self.upload_file(FLASH_SAMPLE_01)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')

    def test_file_content_not_modified(self):
        self.upload_file(FLASH_SAMPLE_02)
        self.assertEqual(Sample.objects.all()[0].sha1, 'eb19009c086845d0408c52d495187380c5762b8c')


class ReprocessAPITest(APITestCase):
    def setUp(self):
        TaskManager().__mock__()  # to avoid uploading samples for real
        self.upload_file(CSHARP_SAMPLE)
        self.sample = Sample.objects.all()[0]
        TaskManager().__mock__()  # to reset submit sample calls to zero
        CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of TaskManager

    def test_nothing_to_reprocess(self):
        data = {'hashes': [self.sample.md5]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 0)

    def test_reprocess_with_md5(self):
        self.upload_file(CSHARP_SAMPLE)
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.md5]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_reprocess_with_sha1(self):
        self.upload_file(CSHARP_SAMPLE)
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.sha1]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_reprocess_with_sha2(self):
        self.upload_file(CSHARP_SAMPLE)
        Result.objects.update(version=-1)
        data = {'hashes': [self.sample.sha2]}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)

    def test_force_reprocess(self):
        data = {'hashes': [self.sample.md5], 'force_reprocess': True}
        self.client.post('/api/reprocess/', data, format='json')
        self.assertEqual(TaskManager().__mock_calls_submit_sample__(), 1)
