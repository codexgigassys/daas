from django.db import transaction, IntegrityError

from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ...models import Sample
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, TEXT_SAMPLE, ZIP, ZIP_PROTECTED


class UploadFileTest(NonTransactionalLiveServerTestCase):
    def setUp(self):
        TaskManager().__mock__()

    def test_file_correctly_uploaded(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/index')

    def test_file_already_uploaded(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.wait_sample_creation(1)
        try:
            with transaction.atomic():
                response = self.upload_file_through_web_view(CSHARP_SAMPLE, follow=True)
                self.wait_sample_creation(2)
        except IntegrityError:
            pass
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/file_already_uploaded')

    def test_upload_file_with_without_filter(self):
        response = self.upload_file_through_web_view(TEXT_SAMPLE)
        self.wait_sample_creation(1)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(response.url, '/index')

    def test_multiple_files_correctly_uploaded(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        response = self.upload_file_through_web_view(FLASH_SAMPLE_01)
        self.wait_sample_creation(2)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/index')

    def test_zip_correctly_uploaded(self):
        response = self.upload_file_through_web_view(ZIP)
        self.wait_sample_creation(2)
        # The zip contains two samples
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/index')

    def test_zip_with_password_correctly_uploaded(self):
        response = self.upload_file_through_web_view(ZIP_PROTECTED, zip_password='ASDF1234')
        self.wait_sample_creation(2)
        # The zip contains two samples
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/index')

    def test_file_types_detected_correctly(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        response = self.upload_file_through_web_view(FLASH_SAMPLE_01)
        self.wait_sample_creation(2)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')
        self.assertEqual(Sample.objects.all()[1].file_type, 'pe')
        self.assertEqual(response.url, '/index')
