from __future__ import annotations
from django.db import models
import logging
from django.db.models import Max
from typing import Optional
from django.conf import settings
from pyseaweed import WeedFS

from ..utils.status import ResultStatus
from ..utils.configuration_manager import ConfigurationManager, Configuration
#from .sample import Sample


class ResultQuerySet(models.QuerySet):

    def failed(self) -> ResultQuerySet:
        return self.filter(status=ResultStatus.FAILED.value)

    def decompiled(self) -> ResultQuerySet:
        return self.filter(status=ResultStatus.SUCCESS.value)

    def timed_out(self) -> ResultQuerySet:
        return self.filter(status=ResultStatus.TIMED_OUT.value)

    def max_elapsed_time(self) -> int:
        max_elapsed_time = self.decompiled().aggregate(Max('elapsed_time'))['elapsed_time__max']
        return max_elapsed_time if max_elapsed_time is not None else 0


class Result(models.Model):
    class Meta:
        permissions = (('update_statistics_permission', 'Update Statistics'),)

    timeout = models.SmallIntegerField(default=None, blank=True, null=True)
    elapsed_time = models.PositiveSmallIntegerField(default=None, blank=True, null=True)
    exit_status = models.SmallIntegerField(default=None, blank=True, null=True)
    status = models.PositiveSmallIntegerField(db_index=True)  # fixme: use choices along with charfield
    output = models.CharField(max_length=10100)
    seaweed_result_id = models.CharField(max_length=20)
    decompiler = models.CharField(max_length=100)
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    processed_on = models.DateTimeField(auto_now_add=True)
    version = models.SmallIntegerField(default=0)
    extension = models.CharField(max_length=15)

    objects = ResultQuerySet.as_manager()

    def save(self, *args, **kwargs) -> None:
        # In some strange cases the output was extremely long and higher the limit.
        if len(self.output) > 10100:
            logging.debug('Truncating decompiler output. It is too long.')
            self.output = self.output[:10000] + '\n\n[[[ Output truncated (more than 10000 characters) ]]]'
        super().save(*args, **kwargs)

    @property
    def timed_out(self) -> bool:
        return self.status == ResultStatus.TIMED_OUT.value

    @property
    def failed(self) -> bool:
        return self.status == ResultStatus.FAILED.value

    @property
    def decompiled(self) -> bool:
        return self.status == ResultStatus.SUCCESS.value

    @property
    def file_type(self) -> str:
        return self.sample.file_type

    @property
    def get_config(self) -> Optional[Configuration]:
        return ConfigurationManager().get_configuration(self.file_type)

    @property
    def decompiled_with_latest_version(self) -> bool:
        return self.version >= self.get_config.version

    @property
    def compressed_source_code(self) -> bytes:
        return WeedFS(settings.SEAWEEDFS_IP, settings.SEAWEEDFS_PORT).get_file(self.seaweed_result_id)

    # Delete seaweedfs source code file.
    def delete(self, *args, **kwargs) -> None:
        logging.error('CG-194 result.py: delete()')
        WeedFS(settings.SEAWEEDFS_IP, settings.SEAWEEDFS_PORT).delete_file(self.seaweed_result_id)
        super().delete(*args, **kwargs)


