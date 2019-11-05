from ..test_utils.test_cases.generic import TestCase
from ...utils.status import TaskStatus
from ...models import Task
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, TEXT_SAMPLE


class JobStatusTest(TestCase):
    def setUp(self):
        TaskManager().__mock__()

    def get_last_task(self):
        return Task.objects.last()

    def test_task_created(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    def test_task_queued(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.get_last_task().status, TaskStatus.QUEUED.value)

    def test_task_processing(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        self.assertEqual(self.get_last_task().status, TaskStatus.PROCESSING.value)

    def test_task_finished(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        TaskManager().get_task('mock').finish()
        self.assertTrue(self.get_last_task().finished())

    def test_task_failed(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        TaskManager().get_task('mock').fail()
        self.assertEqual(self.get_last_task().status, TaskStatus.FAILED.value)

    def test_cancel_queued_task(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.get_last_task().cancel()
        self.assertEqual(self.get_last_task().status, TaskStatus.CANCELLED.value)

    def test_unable_to_cancel_processing_task(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        self.get_last_task().cancel()
        self.assertEqual(self.get_last_task().status, TaskStatus.PROCESSING.value)

    def test_unable_to_cancel_finished_task(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        TaskManager().get_task('mock').finish()
        self.get_last_task().cancel()
        self.assertTrue(self.get_last_task().finished())

    def test_unable_to_cancel_failed_task(self):
        response = self.upload_file_through_web_view(CSHARP_SAMPLE)
        self.assertEqual(response.status_code, 302)
        TaskManager().get_task('mock').process()
        TaskManager().get_task('mock').fail()
        self.get_last_task().cancel()
        self.assertEqual(self.get_last_task().status, TaskStatus.FAILED.value)

    def test_no_task_created_for_invalid_file(self):
        response = self.upload_file_through_web_view(TEXT_SAMPLE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/no_filter_found')
        self.assertEqual(Task.objects.count(), 0)
