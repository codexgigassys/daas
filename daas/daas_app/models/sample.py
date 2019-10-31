from django.db import models
import hashlib
from django.db.models import Q
from functools import reduce

from ..utils.charts import StatisticsManager
from ..utils import result_status
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

    def with_hash_in(self, md5s=[], sha1s=[], sha2s=[]):
        return self.filter(Q(md5__in=md5s) | Q(sha1__in=sha1s) | Q(sha2__in=sha2s))

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
        return self.redisjob.status

    def finished(self):
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
        return self.result.decompiled if self.has_result else False

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
