from django.db import transaction, IntegrityError

from .test_utils import CustomTestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, TEXT, ZIP


class UploadFileTest(CustomTestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_file_correctly_uploaded(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/')

    def test_file_already_uploaded(self):
        self.upload_file(CSHARP)
        try:
            with transaction.atomic():
                response = self.upload_file(CSHARP, follow=True)
        except IntegrityError:
            pass
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/file_already_uploaded')

    def test_upload_file_with_without_filter(self):
        response = self.upload_file(TEXT)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(response.url, '/no_filter_found')

    def test_multiple_files_correctly_uploaded(self):
        self.upload_file(CSHARP)
        response = self.upload_file(FLASH)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/')

    def test_zip_correctly_uploaded(self):
        response = self.upload_file(ZIP)
        # The zip contains two samples
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/')

    def test_file_types_detected_correctly(self):
        self.upload_file(CSHARP)
        response = self.upload_file(FLASH)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')
        self.assertEqual(Sample.objects.all()[1].file_type, 'pe')
        self.assertEqual(response.url, '/')
