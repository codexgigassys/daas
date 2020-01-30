from ..test_utils.test_cases.generic import APITestCase, NonTransactionalLiveServerTestCase
from ...models import Sample, Result
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02
from ...utils.callback_manager import CallbackManager


class GetSamplesFromHashTest(APITestCase):
    def setUp(self) -> None:
        self.sample = Sample.objects.create(size=155, md5='a'*32, sha1='b'*40, sha2='c'*64, file_type='flash',
                                            seaweedfs_file_id='3,01637037d6', uploaded_on='2020-01-15',
                                            file_name='flash_sample.swf')

    def test_no_samples(self):
        self.sample.delete()
        response = self.client.get(f'/api/get_sample_from_hash/{"0"*40}', format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_one_sample_using_md5(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.md5}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('md5'), self.sample.md5)

    def test_get_one_sample_using_sha1(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.sha1}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha1'), self.sample.sha1)

    def test_get_one_sample_using_sha2(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.sha2}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha2'), self.sample.sha2)


class UploadAPITest(NonTransactionalLiveServerTestCase):
    def setUp(self):
        TaskManager().disconnect(disconnect_metadata_extractor=False, disconnect_decompilers=True)

    def tearDown(self) -> None:
        """ We need to wipe the db because the test case superclass is non-transactional """
        TaskManager().connect()
        Sample.objects.all().delete()

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
        self.sample = Sample.objects.create(size=155, md5='a'*32, sha1='b'*40, sha2='c'*64, file_type='flash',
                                            seaweedfs_file_id='3,01637037d6', uploaded_on='2020-01-15',
                                            file_name='flash_sample.swf')
        Result.objects.create(status=1, output='', decompiler='decompiler', sample=self.sample,
                              extension='exe', version=0)
        CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of TaskManager

    def tearDown(self) -> None:
        """ We need to wipe the db because the test case superclass is non-transactional """
        Sample.objects.all().delete()
        Result.objects.all().delete()

    def test_reprocess_with_md5(self):
        response = self.reprocess([self.sample.md5])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_reprocess_with_sha1(self):
        response = self.reprocess([self.sample.sha1])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_reprocess_with_sha2(self):
        response = self.reprocess([self.sample.sha2])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_force_reprocess(self):
        response = self.reprocess([self.sample.md5], True)
        self.assertEqual(response.json()['submitted_samples'], 1)
