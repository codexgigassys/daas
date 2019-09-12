from django.db import transaction, IntegrityError

from .test_utils.test_cases.generic import TestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, TEXT_SAMPLE, ZIP


class UploadFileTest(TestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_file_correctly_uploaded(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/index')

    def test_file_already_uploaded(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        try:
            with transaction.atomic():
                response = self.upload_file_through_web_view(CSHARP_SAMPLE, follow=True)
        except IntegrityError:
            pass
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/file_already_uploaded')

    def test_upload_file_with_without_filter(self):
        response = self.upload_file_through_web_view(TEXT_SAMPLE)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(response.url, '/no_filter_found')

    def test_multiple_files_correctly_uploaded(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        response = self.upload_file_through_web_view(FLASH_SAMPLE_01)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/index')

    def test_zip_correctly_uploaded(self):
        response = self.upload_file_through_web_view(ZIP)
        # The zip contains two samples
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/index')

    def test_file_types_detected_correctly(self):
        self.upload_file_through_web_view(CSHARP_SAMPLE)
        response = self.upload_file_through_web_view(FLASH_SAMPLE_01)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')
        self.assertEqual(Sample.objects.all()[1].file_type, 'pe')
        self.assertEqual(response.url, '/index')
