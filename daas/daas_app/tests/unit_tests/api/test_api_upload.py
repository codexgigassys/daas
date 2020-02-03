from ...test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ....models import Sample
from ....utils.task_manager import TaskManager
from ...test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02


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
