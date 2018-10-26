from django.db import models
from .utils import redis_status
from rq import Queue, cancel_job
from redis import Redis
from .utils.redis_manager import RedisManager
import logging


class SampleManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
        for redis_job in queryset:
            redis_job.update()
            # redis_job.save()
        return queryset


class RedisJob(models.Model):
    job_id = models.CharField(db_index=True, max_length=100)
    status = models.CharField(default=redis_status.QUEUED, max_length=len(redis_status.PROCESSING))

    def update(self):
        if not self.finished():
            job = RedisManager().get_job(self.sample.file_type, self.job_id)
            if job is None:
                self.status = redis_status.QUEUED
            elif job.is_finished:
                self.status = redis_status.DONE
            elif job.is_queued:
                self.status = redis_status.QUEUED
            elif job.is_started:
                self.status = redis_status.PROCESSING
            elif job.is_failed:
                self.status = redis_status.FAILED

    def finished(self):
        return self.status in [redis_status.DONE, redis_status.FAILED, redis_status.CANCELLED]

    def cancel(self):
        RedisManager().cancel_job(self.sample.file_type, self.job_id)
        # To avoid race conditions:
        if not self.finished():
            self.status = redis_status.CANCELLED


class Sample(models.Model):
    class Meta:
        ordering = ['-id']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=120, unique=True)
    data = models.BinaryField(default=0, blank=True, null=True)
    size = models.IntegerField()
    date = models.DateField(auto_now=True)
    file_type = models.CharField(max_length=40)
    command_output = models.CharField(default='', max_length=65000, blank=True, null=True)
    redis_job = models.OneToOneField(RedisJob, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def status(self):
        self.redis_job.update()
        return self.redis_job.status

    def finished(self):
        self.redis_job.update()
        return self.redis_job.finished()

    def unfinished(self):
        return not self.finished()

    def cancel_job(self):
        self.redis_job.cancel()

    def delete(self, *args, **kwargs):
        self.cancel_job()
        super().delete(*args, **kwargs)


class Statistics(models.Model):
    timeout = models.IntegerField(default=None, blank=True, null=True)
    elapsed_time = models.IntegerField(default=None, blank=True, null=True)
    exit_status = models.IntegerField(default=None, blank=True, null=True)
    timed_out = models.BooleanField(default=False)
    output = models.CharField(max_length=65000)
    errors = models.CharField(max_length=65000)
    zip_result = models.BinaryField(default=None, blank=True, null=True)
    decompiled = models.BooleanField(default=False)
    decompiler = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
