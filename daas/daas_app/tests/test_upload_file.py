from django.db import transaction, IntegrityError

from .test_utils import CustomTestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, TEXT


class UploadFileTest(CustomTestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_file_correctly_uploaded(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.url, '/')

    def test_file_already_uploaded(self):
        self.upload_file(CSHARP)
        try:
            with transaction.atomic():
                response = self.upload_file(CSHARP, follow=True)
        except IntegrityError:
            pass
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/file_already_uploaded')
        self.assertEqual(Sample.objects.count(), 1)

    def test_upload_file_with_without_filter(self):
        response = self.upload_file(TEXT)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/no_filter_found')
        self.assertEqual(Sample.objects.count(), 0)

    def test_multiple_files_correctly_uploaded(self):
        self.upload_file(CSHARP)
        response = self.upload_file(FLASH)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(response.url, '/')
