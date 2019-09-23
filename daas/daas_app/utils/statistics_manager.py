from django_redis import get_redis_connection
from typing import SupportsBytes, List, Tuple

from .singleton import ThreadSafeSingleton


class StatisticsManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.redis = get_redis_connection("default")
        self.fields = ['result.status', 'size', 'uploaded_on', 'result.processed_on']

    def report_uploaded_sample(self, sample):
        """ Use this method after receiving a new sample. If the sample is not new, you should not use this method. """
        self._register_multiple_fields_and_values(sample, [self._get_uploaded_on(sample),
                                                           self._get_size(sample)])

    def report_processed_sample(self, sample):
        """ Use this method after processing or reprocessing a sample. """
        self._register_multiple_fields_and_values(sample, [self._get_status(sample),
                                                           self._get_processed_on(sample),
                                                           self._get_elapsed_time(sample)])

    def revert_processed_sample_report(self, sample):
        """ Use this method to reduce values increased by the old result, except for 'processed_on' """
        self._register_multiple_fields_and_values(sample,
                                                  [self._get_status(sample),
                                                   self._get_elapsed_time(sample)],
                                                  increase=False)

    def _register_multiple_fields_and_values(self, sample, fields_and_values: List[Tuple[str, SupportsBytes]], increase=True):
        for field, value in fields_and_values:
            self._register_field_and_value(sample.file_type, field, value, increase)

    def _register_field_and_value(self, file_type: str, field: str, value: SupportsBytes, increase=True):
        """ For instance, register_at_field(file_type="flash", field="seconds", value="12")
            register that a flash sample needed 12 seconds to be decompiled"""
        self.redis.hincrby(f'{file_type}:{field}', value, 1 if increase else -1)

    def _flush(self):
        """ Use this method only for testing or manually wiping the DB. """
        self.redis.flushall()

    # Methods to get information of sample
    def _get_uploaded_on(self, sample):
        return 'uploaded_on', sample.uploaded_on.date().isoformat()

    def _get_size(self, sample):
        return 'size', sample.size

    def _get_status(self, sample):
        return 'status', sample.result.status

    def _get_processed_on(self, sample):
        return 'processed_on', sample.result.processed_on.date().isoformat()

    def _get_elapsed_time(self, sample):
        return 'elapsed_time', sample.result.elapsed_time
