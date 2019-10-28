from django.db import models
import hashlib
import logging
from django.db.models import Q, Max
from functools import reduce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .utils.charts import StatisticsManager
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

    def with_file_type_in(self, file_types):
        return self.filter(file_type__in=file_types)

    def create(self, name, content, file_type=None):
        md5 = hashlib.md5(content).hexdigest()
        sha1 = hashlib.sha1(content).hexdigest()
        sha2 = hashlib.sha256(content).hexdigest()
        return super().create(_data=(content if SAVE_SAMPLES else None), md5=md5, sha1=sha1, sha2=sha2,
                              size=len(content), name=name, file_type=file_type)

    def get_or_create(self, sha1, name, content, identifier):
        already_exists = self.filter(sha1=sha1).exists()
        if already_exists:
            sample = self.get(sha1=sha1)
        else:
            sample = self.create(name, content, identifier)
        return already_exists, sample

    def with_hash_in(self, hashes):
        md5s = self.__get_hashes_of_type(hashes, 'md5')
        sha1s = self.__get_hashes_of_type(hashes, 'sha1')
        sha2s = self.__get_hashes_of_type(hashes, 'sha2')
        return self.filter(Q(md5__in=md5s) | Q(sha1__in=sha1s) | Q(sha2__in=sha2s))

    def get_sample_with_hash(self, hash):
        query = Q()
        query.children = [(self.__get_hash_type(hash), hash)]  # it's better to do this than an eval due to security reasons.
        return self.get(query)

    def __get_hashes_of_type(self, hashes, hash_type):
        return [hash for hash in hashes if self.__get_hash_type(hash) == hash_type]

    def __get_hash_type(self, hash):
        lengths_and_types = {32: 'md5', 40: 'sha1', 64: 'sha2'}
        return lengths_and_types[len(hash)]

    @property
    def __processed_with_old_decompiler_version_query(self):
        query_parts = [(Q(result__version__lt=configuration.version) & Q(file_type=configuration.identifier)) for configuration in ConfigurationManager().get_configurations()]
        return reduce(lambda q1, q2: q1 | q2, query_parts)

    def processed_with_old_decompiler_version(self):
        return self.filter(self.__processed_with_old_decompiler_version_query)

    def processed_with_current_decompiler_version(self):
        return self.exclude(self.__processed_with_old_decompiler_version_query)


class Sample(models.Model):
    class Meta:
        ordering = ['-id']
        permissions = (('download_sample_permission', 'Download Sample'),
                       ('download_source_code_permission', 'Download Source Code'),
                       ('upload_sample_permission', 'Upload Sample'),
                       ('delete_sample_permission', 'Delete Sample'),)

    # MD5 is weak, so it's better to not use unique=True here.
    md5 = models.CharField(max_length=32, db_index=True)
    sha1 = models.CharField(max_length=40, unique=True)
    sha2 = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=300)
    # We do not need unique here because sha1 constraint will raise an exception instead.
    _data = models.BinaryField(default=0, blank=True, null=True)
    size = models.IntegerField()
    uploaded_on = models.DateTimeField(auto_now_add=True, db_index=True)
    # The identifier set for that kind of file. Not the mime type.
    file_type = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    objects = SampleQuerySet.as_manager()

    def __str__(self):
        return "%s (type: %s, sha1: %s)" % (self.name, self.file_type, self.sha1)

    def status(self):
        self.redisjob.update()
        return self.redisjob.status

    def finished(self):
        self.redisjob.update()
        return self.redisjob.finished()

    def unfinished(self):
        return not self.finished()

    def cancel_job(self):
        try:
            self.redisjob.cancel()
        except AttributeError:
            pass

    def delete(self, *args, **kwargs):
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

    def is_possible_to_reprocess(self):
        return self.finished() and self.content_saved()

    @property
    def requires_processing(self):
        """ Returns True if the the sample was not processed or it was processed with an old decompiler. """
        try:
            return not self.result.decompiled_with_latest_version
        except AttributeError:
            # It was not processed
            return True

    @property
    def source_code(self):
        try:
            return self.result.compressed_source_code
        except AttributeError:
            return None

    @property
    def has_redis_job(self):
        return hasattr(self, 'redisjob')

    @property
    def has_result(self):
        return hasattr(self, 'result')

    @property
    def data(self):
        try:
            return self._data.tobytes()
        except AttributeError:
            return self._data

    def wipe(self):
        if self.has_redis_job:
            self.redisjob.delete()
        if self.has_result:
            StatisticsManager().revert_processed_sample_report(self)
            self.result.delete()


class ResultQuerySet(models.QuerySet):

    def failed(self):
        return self.filter(status=result_status.FAILED)

    def decompiled(self):
        return self.filter(status=result_status.SUCCESS)

    def timed_out(self):
        return self.filter(status=result_status.TIMED_OUT)

    def max_elapsed_time(self):
        max_elapsed_time = self.decompiled().aggregate(Max('elapsed_time'))['elapsed_time__max']
        return max_elapsed_time if max_elapsed_time is not None else 0


class Result(models.Model):
    class Meta:
        permissions = (('update_statistics_permission', 'Update Statistics'),)

    timeout = models.SmallIntegerField(default=None, blank=True, null=True)
    elapsed_time = models.PositiveSmallIntegerField(default=None, blank=True, null=True)
    exit_status = models.SmallIntegerField(default=None, blank=True, null=True)
    status = models.PositiveSmallIntegerField(db_index=True)  # fixme: usar choices y charfield
    output = models.CharField(max_length=10100)
    compressed_source_code = models.BinaryField(default=None, blank=True, null=True)
    decompiler = models.CharField(max_length=100)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    processed_on = models.DateTimeField(auto_now_add=True)
    version = models.SmallIntegerField(default=0)
    extension = models.CharField(max_length=15)

    objects = ResultQuerySet.as_manager()

    def save(self, *args, **kwargs):
        # In some strange cases the output was extremely long and higher the limit.
        if len(self.output) > 10100:
            logging.debug('Truncating decompiler output. It is too long.')
            self.output = self.output[:10000] + '\n\n[[[ Output truncated (more than 10000 characters) ]]]'
        super().save(*args, **kwargs)

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
        return self.version == self.get_config.version


class RedisJob(models.Model):
    class Meta:
        permissions = (('cancel_job_permission', 'Cancel Job'),)

    job_id = models.CharField(max_length=100)
    status = models.CharField(default=redis_status.QUEUED, max_length=len(redis_status.PROCESSING))
    created_on = models.DateTimeField(auto_now_add=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)

    def __set_status(self, status):
        # If we don't use 'save' method here, race conditions might happen, leading to incorrect status.
        logging.debug('Redis job %s changing status: %s -> %s' % (self.job_id, self.status, status))
        self.status = status
        self.save()

    def update(self):
        if not self.finished():
            job = RedisManager().get_job(self.sample.file_type, self.job_id)
            if job is None:
                self.__set_status(redis_status.DONE if self.sample.decompiled else redis_status.FAILED)
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


# Signals
@receiver(post_save, sender=Sample)
def report_created_sample_for_statistics(sender, instance, created, **kwargs):
    if created:
        StatisticsManager().report_uploaded_sample(instance)


@receiver(post_save, sender=Result)
def report_sample_result_for_statistics(sender, instance, created, **kwargs):
    if created:
        StatisticsManager().report_processed_sample(instance.sample)


@receiver(post_delete, sender=Result)
def revert_sample_result_for_statistics(sender, instance, **kwargs):
    StatisticsManager().revert_processed_sample_report(instance.sample)
