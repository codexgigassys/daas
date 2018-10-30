from django.db import models
from .utils import redis_status
from .utils.redis_manager import RedisManager
from .config import ALLOW_SAMPLE_DOWNLOAD
import logging
from .decompilers.decompiler_config import configs


class SampleManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        for redis_job in queryset:
            redis_job.update()
        return queryset


class Sample(models.Model):
    class Meta:
        ordering = ['-id']
    # MD5 is weak, so it's better to not use unique=True here.
    md5 = models.CharField(max_length=100, db_index=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    # We do not need unique here because sha1 constraint will raise an exception instead.
    data = models.BinaryField(default=0, blank=True, null=True)
    size = models.IntegerField()
    date = models.DateField(auto_now=True)
    file_type = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.name

    def redis_job(self):
        return RedisJob.objects.filter(sample=self).latest('date')

    def status(self):
        self.redis_job().update()
        return self.redis_job().status

    def finished(self):
        self.redis_job().update()
        return self.redis_job().finished()

    def unfinished(self):
        return not self.finished()

    def cancel_job(self):
        self.redis_job().cancel()

    def delete(self, *args, **kwargs):
        self.cancel_job()
        super().delete(*args, **kwargs)

    def decompiled(self):
        try:
            return self.statistics.decompiled
        except AttributeError:
            return False

    def content_saved(self):
        return self.data is not None

    def downloadable(self):
        return self.content_saved() and ALLOW_SAMPLE_DOWNLOAD


class Statistics(models.Model):
    timeout = models.IntegerField(default=None, blank=True, null=True, db_index=True)
    elapsed_time = models.IntegerField(default=None, blank=True, null=True, db_index=True)
    exit_status = models.IntegerField(default=None, blank=True, null=True, db_index=True)
    # In most cases (99%+) it will be False, so it makes sense to create an index of a boolean column
    timed_out = models.BooleanField(default=False, db_index=True)
    output = models.CharField(max_length=65000)
    errors = models.CharField(max_length=65000)
    zip_result = models.BinaryField(default=None, blank=True, null=True)
    # In most cases (99%+) it will be True, so it makes sense to create an index of a boolean column
    decompiled = models.BooleanField(default=False, db_index=True)
    decompiler = models.CharField(max_length=100, db_index=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    version = models.IntegerField(default=0, db_index=True)

    def file_type(self):
        return self.sample.file_type

    def get_config(self):
        for config in configs:
            if config['identifier'] == self.file_type():
                return config
        raise Exception('Missing configuration with identifier: %s' % self.file_type())

    def decompiled_with_latest_version(self):
        return self.version == self.get_config().get('version', 0)


class RedisJob(models.Model):
    job_id = models.CharField(db_index=True, max_length=100)
    status = models.CharField(default=redis_status.QUEUED, max_length=len(redis_status.PROCESSING))
    date = models.DateField(auto_now=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)

    def __set_status(self, status):
        # If we don't use 'save' method here, race conditions will happen and lead to incorrect status.
        logging.debug('Redis job %s changing status: %s -> %s' % (self.job_id, self.status, status))
        self.status = status
        self.save()

    def update(self):
        if not self.finished():
            job = RedisManager().get_job(self.sample.file_type, self.job_id)
            if job is None:
                self.__set_status(redis_status.DONE if self.sample.decompiled() else redis_status.FAILED)
            elif job.is_finished:
                self.__set_status(redis_status.DONE)
            elif job.is_queued:
                self.__set_status(redis_status.QUEUED)
            elif job.is_started:
                self.__set_status(redis_status.PROCESSING)
            elif job.is_failed:
                self.__set_status(redis_status.FAILED)

    def finished(self):
        return self.status in [redis_status.DONE, redis_status.FAILED, redis_status.CANCELLED]

    def is_cancellable(self):
        return self.status == redis_status.QUEUED

    def is_cancelled(self):
        return self.status == redis_status.CANCELLED

    def cancel(self):
        if self.is_cancellable():
            RedisManager().cancel_job(self.sample.file_type, self.job_id)
            self.__set_status(redis_status.CANCELLED)
