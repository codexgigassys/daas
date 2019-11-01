from django.db import models
import logging


from ..utils.status import TaskStatus
from ..utils.redis_manager import RedisManager
from .sample import Sample


class RedisJob(models.Model):
    class Meta:
        permissions = (('cancel_job_permission', 'Cancel Job'),)

    job_id = models.CharField(max_length=100)
    _status = models.IntegerField(default=TaskStatus.QUEUED.value)
    created_on = models.DateTimeField(auto_now_add=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)

    def _set_status(self, new_status: TaskStatus) -> None:
        logging.debug('Redis job %s changing status: %s -> %s' % (self.job_id, self._status, new_status))
        self._status = new_status.value
        self.save()

    def update_status(self) -> None:
        if not self._finished():
            job = RedisManager().get_job(self.sample.file_type, self.job_id)
            if job is None or job.is_finished:
                self._set_status(TaskStatus.DONE)
            elif job.is_queued:
                self._set_status(TaskStatus.QUEUED)
            elif job.is_started:
                self._set_status(TaskStatus.PROCESSING)
            elif job.is_failed:
                self._set_status(TaskStatus.FAILED)

    @property
    def status(self) -> str:
        self.update_status()
        return self._status

    @property
    def status_as_string(self):
        status_name = TaskStatus(self.status).name
        return f'{status_name[0]}{status_name[1:].lower()}'

    def _finished(self):
        return self._status in [TaskStatus.DONE.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]

    def finished(self):
        self.update_status()
        return self._finished()

    def is_cancellable(self):
        return self.status == TaskStatus.QUEUED.value

    def is_cancelled(self):
        return self.status == TaskStatus.CANCELLED.value

    def cancel(self):
        if self.is_cancellable():
            RedisManager().cancel_job(self.sample.file_type, self.job_id)
            self._set_status(TaskStatus.CANCELLED)
