from django.db import transaction, IntegrityError

from .test_utils import CustomTestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager


CSHARP = '/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'
TEXT = '/daas/daas/daas_app/tests/resources/text.txt'
FLASH = '/daas/daas/daas_app/tests/resources/995bb44df3d6b31d9422ddb9f3f78b7b.flash'


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
