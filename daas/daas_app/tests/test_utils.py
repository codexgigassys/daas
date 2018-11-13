from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from ..views import upload_file


class CustomTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.factory = RequestFactory()
        self.user = self.__get_or_create_user()
        super().__init__(*args, **kwargs)

    def __get_or_create_user(self):
        if User.objects.filter(username='daas').count() > 0:
            user = User.objects.get(username='daas')
        else:
            user = User.objects.create_user(username='daas', email='daas@mail.com', password='top_secret')
        return user

    def upload_file(self, file_name, follow=False):
        with File(open(file_name, 'rb')) as file:
            uploaded_file = SimpleUploadedFile('460f0c273d1dc133ed7ac1e24049ac30.csharp', file.read(),
                                               content_type='multipart/form-data')
            request = self.factory.post('upload_file/', follow=follow)
            request.FILES['file'] = uploaded_file
        request.user = self.user
        return upload_file(request)


def generate_worker_result(sample, timeout=120, elapsed_time=5, failed=False, decompiler_name='mock decompiler'):
    timed_out = elapsed_time >= timeout
    exit_status = 124 if timed_out else (1 if failed else 0)
    info_for_statistics = {'sha1': sample.sha1,
                           'timeout': timeout,
                           'elapsed_time': elapsed_time + 1,
                           'exit_status': exit_status,
                           'timed_out': timed_out,
                           'output': 'decompiler output',
                           'decompiled': exit_status == 0,
                           'decompiler': decompiler_name,
                           'version': 1}
    return {'statistics': info_for_statistics, 'zip': 'fake zip'}
