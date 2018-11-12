from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction, IntegrityError

from ..models import Sample
from ..views import upload_file


class UploadFileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='daas', email='daas@mail.com', password='top_secret')

    def upload_file(self, follow=False):
        with File(open('/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp', 'rb')) as file:
            uploaded_file = SimpleUploadedFile('460f0c273d1dc133ed7ac1e24049ac30.csharp', file.read(),
                                               content_type='multipart/form-data')
            request = self.factory.post('upload_file/', follow=follow)
            request.FILES['file'] = uploaded_file
        request.user = self.user
        return upload_file(request)

    def test_file_correctly_uploaded(self):
        response = self.upload_file()
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_file_already_uploaded(self):
        self.upload_file()
        try:
            with transaction.atomic():
                response = self.upload_file(follow=True)
        except IntegrityError:
            pass
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/file_already_uploaded')
