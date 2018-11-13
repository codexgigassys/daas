from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction, IntegrityError

from ..models import Sample
from ..views import upload_file
from ..utils.redis_manager import RedisManager


CSHARP = '/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'
TEXT = '/daas/daas/daas_app/tests/resources/text.txt'
FLASH = '/daas/daas/daas_app/tests/resources/995bb44df3d6b31d9422ddb9f3f78b7b.flash'


class UploadFileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='daas', email='daas@mail.com', password='top_secret')
        RedisManager().__mock__()

    def upload_file(self, file_name, follow=False):
        with File(open(file_name, 'rb')) as file:
            uploaded_file = SimpleUploadedFile('460f0c273d1dc133ed7ac1e24049ac30.csharp', file.read(),
                                               content_type='multipart/form-data')
            request = self.factory.post('upload_file/', follow=follow)
            request.FILES['file'] = uploaded_file
        request.user = self.user
        return upload_file(request)

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
