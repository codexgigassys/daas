from ..test_utils.test_cases.generic import TestCase
from ...utils.status import TaskStatus
from ...models import RedisJob
from ...utils.redis_manager import RedisManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, TEXT_SAMPLE


class JobStatusTest(TestCase):
    def setUp(self):
        RedisManager().__mock__()

    def get_last_job(self):
        return RedisJob.objects.last()

    def test_redis_job_created(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RedisJob.objects.count(), 1)

    def job_queued(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.get_last_job().status, TaskStatus.QUEUED.value)

    def test_job_processing(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.assertEqual(self.get_last_job().status, TaskStatus.PROCESSING.value)

    def test_job_finished(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.assertTrue(self.get_last_job().finished())

    def test_job_failed(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.assertEqual(self.get_last_job().status, TaskStatus.FAILED.value)

    def test_cancel_queued_job(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, TaskStatus.CANCELLED.value)

    def test_unable_to_cancel_processing_job(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, TaskStatus.PROCESSING.value)

    def test_unable_to_cancel_finished_job(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').finish()
        self.get_last_job().cancel()
        self.assertTrue(self.get_last_job().finished())

    def test_unable_to_cancel_failed_job(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        RedisManager().get_job('mock').process()
        RedisManager().get_job('mock').fail()
        self.get_last_job().cancel()
        self.assertEqual(self.get_last_job().status, TaskStatus.FAILED.value)

    def test_no_job_created_for_invalid_file(self):
        response = self.upload_file_through_web_view(TEXT_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/no_filter_found')
        self.assertEqual(RedisJob.objects.count(), 0)
