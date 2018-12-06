from django.db import models
import hashlib
import logging
from django.db.models import Count, DateField
from django.db.models.functions import Trunc
from django.db.models import Q

from .utils import redis_status, result_status
from .utils.redis_manager import RedisManager
from .config import ALLOW_SAMPLE_DOWNLOAD, SAVE_SAMPLES
from .utils.configuration_manager import ConfigurationManager


class SampleQuerySet(models.QuerySet):
    def with_size_between(self, size_from, size_to):
        """ Returns all samples which size is in between [size_from, size_to) """
        return self.filter(size__gte=size_from, size__lt=size_to)

    def with_elapsed_time_between(self, elapsed_time_from_, elapsed_time_to):
        return self.filter(result__elapsed_time__gte=elapsed_time_from_,
                           result__elapsed_time__lte=elapsed_time_to)

    def failed(self):
        return self.filter(result__status=result_status.FAILED)

    def decompiled(self):
        return self.filter(result__status=result_status.SUCCESS)

    def timed_out(self):
        return self.filter(result__status=result_status.TIMED_OUT)

    def finished(self):
        return self.exclude(result__isnull=True)

    def with_file_type(self, file_type):
        return self.filter(file_type=file_type)

    def classify_by_file_type(self, count=False):
        result = {}
        for file_type in ConfigurationManager().get_identifiers():
            query_set = self.with_file_type(file_type)
            result.update({file_type: query_set.count() if count else query_set})
        return result

    def samples_per_upload_date(self):
        return self.__count_per_date('uploaded_on')

    def samples_per_process_date(self):
        return self.__count_per_date('result__processed_on')

    def __count_per_date(self, date_):
        # We need an order_by here because Sample class has a default order_by. See:
        # https://docs.djangoproject.com/en/2.1/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        return self.annotate(date=Trunc(date_, 'day', output_field=DateField())).values('date').annotate(count=Count('*')).order_by()
        count_dict = {}
        for element in counts:
            if element['date'] is not None:
                count_dict[element['date']] = element['count']
        return count_dict

    def first_date(self):
        return self.last().uploaded_on.date()

    def custom_create(self, name, content, file_type=None):
        md5 = hashlib.md5(content).hexdigest()
        sha1 = hashlib.sha1(content).hexdigest()
        sha2 = hashlib.sha256(content).hexdigest()
        return self.create(data=(content if SAVE_SAMPLES else None), md5=md5, sha1=sha1, sha2=sha2,
                           size=len(content), name=name, file_type=file_type)

    def with_hash_in(self, md5s=[], sha1s=[], sha2s=[]):
        return self.filter(Q(md5__in=md5s) | Q(sha1__in=sha1s) | Q(sha2__in=sha2s))


class Sample(models.Model):
    class Meta:
        ordering = ['-id']
    # MD5 is weak, so it's better to not use unique=True here.
    md5 = models.CharField(max_length=32, db_index=True)
    sha1 = models.CharField(max_length=40, unique=True)
    sha2 = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=300)
    # We do not need unique here because sha1 constraint will raise an exception instead.
    data = models.BinaryField(default=0, blank=True, null=True)
    size = models.IntegerField()
    uploaded_on = models.DateTimeField(auto_now=True, db_index=True)
    # The identifier set for that kind of file. Not the mime type.
    file_type = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    objects = SampleQuerySet.as_manager()

    def __str__(self):
        return self.name

    def all_redis_jobs(self):
        return RedisJob.objects.filter(sample=self)

    def redis_job(self):
        return self.all_redis_jobs().latest('created_on')

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
        if self.all_redis_jobs().count() > 0:
            self.cancel_job()
        super().delete(*args, **kwargs)

    @property
    def decompiled(self):
        try:
            return self.result.decompiled
        except AttributeError:
            return False

    def content_saved(self):
        return self.data is not None

    def downloadable(self):
        return self.content_saved() and ALLOW_SAMPLE_DOWNLOAD


class ResultQuerySet(models.QuerySet):

    def failed(self):
        return self.filter(status=result_status.FAILED)

    def decompiled(self):
        return self.filter(status=result_status.SUCCESS)

    def timed_out(self):
        return self.filter(status=result_status.TIMED_OUT)


class Result(models.Model):
    timeout = models.SmallIntegerField(default=None, blank=True, null=True)
    elapsed_time = models.PositiveSmallIntegerField(default=None, blank=True, null=True)
    exit_status = models.SmallIntegerField(default=None, blank=True, null=True)
    status = models.PositiveSmallIntegerField(db_index=True)
    output = models.CharField(max_length=65000)
    zip_result = models.BinaryField(default=None, blank=True, null=True)
    decompiler = models.CharField(max_length=100)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    processed_on = models.DateTimeField(auto_now=True, db_index=True)
    version = models.SmallIntegerField(default=0)

    objects = ResultQuerySet.as_manager()

    @property
    def timed_out(self):
        return self.status == result_status.TIMED_OUT

    @property
    def failed(self):
        return self.status == result_status.FAILED

    @property
    def decompiled(self):
        return self.status == result_status.SUCCESS

    @property
    def file_type(self):
        return self.sample.file_type

    @property
    def get_config(self):
        return ConfigurationManager().get_configuration(self.file_type)

    @property
    def decompiled_with_latest_version(self):
        return self.version == self.get_config().version


class RedisJob(models.Model):
    job_id = models.CharField(db_index=True, max_length=100)
    status = models.CharField(default=redis_status.QUEUED, max_length=len(redis_status.PROCESSING))
    created_on = models.DateTimeField(auto_now=True)
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
