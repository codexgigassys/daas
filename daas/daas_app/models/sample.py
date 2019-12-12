from django.db import models
import hashlib
from django.db.models import Q
from functools import reduce

from ..utils.status import TaskStatus, SampleStatus, ResultStatus
from ..config import ALLOW_SAMPLE_DOWNLOAD, SAVE_SAMPLES
from ..utils.configuration_manager import ConfigurationManager


class SampleQuerySet(models.QuerySet):
    def with_size_between(self, size_from, size_to):
        """ Returns all samples which size is in between [size_from, size_to) """
        return self.filter(size__gte=size_from, size__lt=size_to)

    def with_elapsed_time_between(self, elapsed_time_from_, elapsed_time_to):
        return self.filter(result__elapsed_time__gte=elapsed_time_from_,
                           result__elapsed_time__lte=elapsed_time_to)

    def failed(self):
        return self.filter(result__status=ResultStatus.FAILED.value)

    def decompiled(self):
        return self.filter(result__status=ResultStatus.SUCCESS.value)

    def timed_out(self):
        return self.filter(result__status=ResultStatus.TIMED_OUT.value)

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
    seaweedfs_file_id = models.CharField(max_length=20)

    objects = SampleQuerySet.as_manager()

    def __str__(self):
        return "%s (type: %s, sha1: %s)" % (self.name, self.file_type, self.sha1)

    def delete(self, *args, **kwargs):
        self.cancel_task()
        super().delete(*args, **kwargs)

    @property
    def _result_status(self) -> int:
        # The refresh is to really known if this instance has a result or not,
        # because the result might be added minutes after this instance has been instantiated.
        self.refresh_from_db()
        return self.result.status if self.has_result else ResultStatus.NO_RESULT.value

    @property
    def _task_status(self) -> int:
        return self.task.status if self.has_task else TaskStatus.NO_TASK.value

    @property
    def status(self) -> SampleStatus:
        """ Based on the status of both the task and the result, returns the status
            of the sample.
            To not write lot of lines with non-understandable tons of nested IFs statements,
            this method explicitly states all cases on an organized matrix.
            Note: When a worker is sending the result, task_status=PROCESSING and the result is being created.
                  After the result creation finishes, there is a small timeframe until the task is marked as DONE.
                  To avoid race conditions on those cases, the sample status will be the result status. """
        # TaskStatus, SampleStatus, ResultStatus
        # Result status:        SUCCESS              TIMED_OUT               FAILED              NO_RESULT            # Task status
        combinations = [[SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.QUEUED],      # QUEUED
                        [SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.CANCELLED],   # CANCELLED
                        [SampleStatus.DONE, SampleStatus.TIMED_OUT, SampleStatus.FAILED, SampleStatus.PROCESSING],    # PROCESSING
                        [SampleStatus.DONE, SampleStatus.TIMED_OUT, SampleStatus.FAILED, SampleStatus.INVALID],       # DONE
                        [SampleStatus.FAILED, SampleStatus.FAILED, SampleStatus.FAILED, SampleStatus.FAILED],         # FAILED
                        [SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.INVALID, SampleStatus.INVALID]]     # NO_TASK
        return combinations[self._task_status][self._result_status]

    @property
    def requires_processing(self) -> bool:
        """ Returns True if the the sample was not processed or it was processed with an old decompiler. """
        return not self.result.decompiled_with_latest_version if self.has_result else True

    @property
    def source_code(self):
        return self.result.compressed_source_code if self.has_result else None

    @property
    def has_task(self):
        return hasattr(self, 'task')

    @property
    def has_result(self):
        return hasattr(self, 'result')

    @property
    def data(self):
        try:
            return self._data.tobytes()
        except AttributeError:
            return self._data

    @property
    def decompiled(self):
        return self.status == SampleStatus.DONE

    def finished(self):
        return self.status in [SampleStatus.DONE, SampleStatus.FAILED, SampleStatus.TIMED_OUT, SampleStatus.CANCELLED]

    def unfinished(self):
        return not self.finished()

    def cancel_task(self):
        if self.has_task:
            self.task.cancel()

    def content_saved(self):
        return self.data is not None

    def downloadable(self):
        return self.content_saved() and ALLOW_SAMPLE_DOWNLOAD

    def is_possible_to_reprocess(self):
        return self.finished() and self.content_saved()

    def wipe(self):
        if self.has_task:
            self.task.delete()
        if self.has_result:
            self.result.delete()
