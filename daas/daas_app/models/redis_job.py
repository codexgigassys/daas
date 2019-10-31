from django.db import models
import logging


from ..utils import redis_status
from ..utils.redis_manager import RedisManager
from .sample import Sample


class RedisJob(models.Model):
    class Meta:
        permissions = (('cancel_job_permission', 'Cancel Job'),)

    job_id = models.CharField(max_length=100)
    _status = models.CharField(default=redis_status.QUEUED, max_length=len(redis_status.PROCESSING))
    created_on = models.DateTimeField(auto_now_add=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)

    def _set_status(self, new_status: str) -> None:
        logging.debug('Redis job %s changing status: %s -> %s' % (self.job_id, self._status, new_status))
        self._status = new_status
        self.save()

    def update_status(self) -> None:
        if not self._finished():
            job = RedisManager().get_job(self.sample.file_type, self.job_id)
            if job is None:
                self._set_status(redis_status.DONE)
            elif job.is_finished:
                self._set_status(redis_status.DONE if self.sample.has_result else redis_status.FAILED)
            elif job.is_queued:
                self._set_status(redis_status.QUEUED)
            elif job.is_started:
                self._set_status(redis_status.PROCESSING)
            elif job.is_failed:
                self._set_status(redis_status.FAILED)

    @property
    def status(self) -> str:
        self.update_status()
        return self._status

    def _finished(self):
        return self._status in [redis_status.DONE, redis_status.FAILED, redis_status.CANCELLED]

    def finished(self):
        self.update_status()
        return self._finished()

    def is_cancellable(self):
        return self.status == redis_status.QUEUED

    def is_cancelled(self):
        return self.status == redis_status.CANCELLED

    def cancel(self):
        if self.is_cancellable():
            RedisManager().cancel_job(self.sample.file_type, self.job_id)
            self._set_status(redis_status.CANCELLED)
