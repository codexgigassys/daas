from django.db import models
import logging

from ..utils.status import TaskStatus
from ..utils.task_manager import TaskManager
from .sample import Sample


class Task(models.Model):
    class Meta:
        permissions = (('cancel_task_permission', 'Cancel Task'),)

    task_id = models.CharField(max_length=100)
    _status = models.IntegerField(default=TaskStatus.QUEUED.value)
    created_on = models.DateTimeField(auto_now_add=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, related_name='task')

    def _set_status(self, new_status: TaskStatus) -> None:
        logging.debug('Redis task %s changing status: %s -> %s' % (self.task_id, self._status, new_status))
        self._status = new_status.value
        self.save()

    def update_status(self) -> None:
        if not self._finished():
            task = TaskManager().get_task(self.sample.file_type, self.task_id)
            if task is None or task.is_finished:
                self._set_status(TaskStatus.DONE)
            elif task.is_queued:
                self._set_status(TaskStatus.QUEUED)
            elif task.is_started:
                self._set_status(TaskStatus.PROCESSING)
            elif task.is_failed:
                self._set_status(TaskStatus.FAILED)

    @property
    def status(self) -> str:
        self.update_status()
        return self._status

    def _finished(self) -> bool:
        return self._status in [TaskStatus.DONE.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]

    def finished(self) -> bool:
        self.update_status()
        return self._finished()

    def is_cancellable(self) -> bool:
        return self.status == TaskStatus.QUEUED.value

    def is_cancelled(self) -> bool:
        return self.status == TaskStatus.CANCELLED.value

    def cancel(self) -> None:
        if self.is_cancellable():
            TaskManager().cancel_task(self.sample.file_type, self.task_id)
            self._set_status(TaskStatus.CANCELLED)
