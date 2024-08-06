from django.http import HttpResponse
import time

from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ...utils.status import TaskStatus
from ...models import Sample, Task, Result
from ...utils.task_manager import TaskManager
from ..test_utils.resource_directories import CSHARP_SAMPLE, TEXT_SAMPLE

# Test run on different classes to avoid port overlapping between tests and guarantee test independence.


class JobStatusTestCase(NonTransactionalLiveServerTestCase):
    def _wipe(self) -> None:
        TaskManager().reset()
        Sample.objects.all().delete()
        Result.objects.all().delete()
        Task.objects.all().delete()

    def setUp(self) -> None:
        """ Flush the DB, because we are using a non-transactional test case. """
        super().setUp()
        self._wipe()

    def tearDown(self) -> None:
        """ Flush the DB, because we are using a non-transactional test case. """
        super().tearDown()
        self._wipe()

    def _get_last_task(self):
        return Task.objects.last()

    def _upload_file_through_web_view_and_wait(self, sample_path: str, new_samples: int = 1) -> HttpResponse:
        response = super().upload_file_through_web_view(sample_path)
        self.assertEqual(response.status_code, 302)
        self.wait_sample_creation(new_samples)
        return response


class JobStatusTestTaskQueued(JobStatusTestCase):
    def test_task_queued(self):
        TaskManager().redirect_decompilation_to_test_queue(True)
        self._upload_file_through_web_view_and_wait(CSHARP_SAMPLE)
        self.assertEqual(self._get_last_task().status, TaskStatus.QUEUED.value)
        self.assertEqual(Task.objects.count(), 1)
        self.wait_result_creation(1)


class JobStatusTestTaskFinished(JobStatusTestCase):
    def test_task_finished(self):
        self._upload_file_through_web_view_and_wait(CSHARP_SAMPLE)
        self.wait_result_creation(1)
        self.assertTrue(self._get_last_task().finished())


class JobStatusTestCancelQueuedTask(JobStatusTestCase):
    def test_cancel_queued_task(self):
        TaskManager().redirect_decompilation_to_test_queue(True)
        self._upload_file_through_web_view_and_wait(CSHARP_SAMPLE)
        self._get_last_task().cancel()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(self._get_last_task().status,
                         TaskStatus.CANCELLED.value)


class JobStatusTestUnableToCancelProcessingTask(JobStatusTestCase):
    def test_unable_to_cancel_processing_task(self):
        self._upload_file_through_web_view_and_wait(CSHARP_SAMPLE)
        counter = 0
        while True:
            counter += 1
            if counter > 200:
                self.assertEqual(self._get_last_task().status, -100)  # make it fail
            if self._get_last_task().status != TaskStatus.PROCESSING.value:
                time.sleep(0.05)
            else:
                break
        self.assertEqual(self._get_last_task().status,
                         TaskStatus.PROCESSING.value)
        self._get_last_task().cancel()
        self.assertEqual(self._get_last_task().status,
                         TaskStatus.PROCESSING.value)
        self.assertEqual(Task.objects.count(), 1)
        # self.wait_result_creation(1)


class JobStatusTestCancelFinishedTask(JobStatusTestCase):
    def test_unable_to_cancel_finished_task(self):
        self._upload_file_through_web_view_and_wait(CSHARP_SAMPLE)
        self.wait_result_creation(1)
        self._get_last_task().cancel()
        self.assertTrue(self._get_last_task().finished())


class JobStatusTestNoTaskCreatedForInvalidFile(JobStatusTestCase):
    def test_no_task_created_for_invalid_file(self):
        response = self._upload_file_through_web_view_and_wait(TEXT_SAMPLE, 0)
        self.assertEqual(response.url, '/index')
        self.assertEqual(Task.objects.count(), 0)
