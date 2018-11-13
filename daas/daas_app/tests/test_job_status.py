from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile


from ..utils.redis_status import FAILED, PROCESSING, QUEUED, DONE, CANCELLED
from ..models import Sample, RedisJob
from ..views import upload_file
from ..utils.redis_manager import RedisManager


CSHARP = '/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'
TEXT = '/daas/daas/daas_app/tests/resources/text.txt'


class JobStatusTest(TestCase):
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

    def get_last_job(self):
        return RedisJob.objects.last()

    def test_redis_job_created(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RedisJob.objects.count(), 1)

    def job_queued(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.get_last_job().status, QUEUED)

    def test_job_processing(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, PROCESSING)

    def test_job_finished(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, DONE)

    def test_job_failed(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, FAILED)

    def test_not_updated_job_is_still_queued(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        # do not update the job
        self.assertEqual(self.get_last_job().status, QUEUED)

    def test_cancel_queued_job(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, CANCELLED)

    def test_unable_to_cancel_processing_job(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, PROCESSING)

    def test_unable_to_cancel_finished_job(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, DONE)

    def test_unable_to_cancel_failed_job(self):
        response = self.upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, FAILED)

    def test_no_job_created_for_invalid_file(self):
        response = self.upload_file(TEXT)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/no_filter_found')
        self.assertEqual(RedisJob.objects.count(), 0)
