from ..test_utils.test_cases.generic import TestCase
from ...utils.redis_status import FAILED, PROCESSING, QUEUED, DONE, CANCELLED
from ...models import RedisJob
from ...utils.redis_manager import RedisManager


CSHARP = '/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'
TEXT = '/daas/daas/daas_app/tests/resources/text.txt'


class JobStatusTest(TestCase):
    def setUp(self):
        RedisManager().__mock__()

    def get_last_job(self):
        return RedisJob.objects.last()

    def test_redis_job_created(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RedisJob.objects.count(), 1)

    def job_queued(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.get_last_job().status, QUEUED)

    def test_job_processing(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, PROCESSING)

    def test_job_finished(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, DONE)

    def test_job_failed(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.get_last_job().update()
        self.assertEqual(self.get_last_job().status, FAILED)

    def test_not_updated_job_is_still_queued(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        # do not update the job
        self.assertEqual(self.get_last_job().status, QUEUED)

    def test_cancel_queued_job(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, CANCELLED)

    def test_unable_to_cancel_processing_job(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, PROCESSING)

    def test_unable_to_cancel_finished_job(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, DONE)

    def test_unable_to_cancel_failed_job(self):
        response = self.upload_file_through_web_view(CSHARP)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.get_last_job().update()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, FAILED)

    def test_no_job_created_for_invalid_file(self):
        response = self.upload_file_through_web_view(TEXT)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/no_filter_found')
        self.assertEqual(RedisJob.objects.count(), 0)
