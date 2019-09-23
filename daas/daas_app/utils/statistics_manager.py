from django_redis import get_redis_connection
from typing import SupportsBytes, List, Tuple

from .singleton import ThreadSafeSingleton


class StatisticsManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self.redis = get_redis_connection("default")
        self.fields = ['result.status', 'size', 'uploaded_on', 'result.processed_on']

    def report_uploaded_sample(self, sample) -> None:
        """ Use this method after receiving a new sample. If the sample is not new, you should not use this method. """
        self._register_multiple_fields_and_values(sample, [self._get_uploaded_on(sample),
                                                           self._get_size(sample)])

    def report_processed_sample(self, sample) -> None:
        """ Use this method after processing or reprocessing a sample. """
        self._register_multiple_fields_and_values(sample, [self._get_status(sample),
                                                           self._get_processed_on(sample),
                                                           self._get_elapsed_time(sample)])

    def revert_processed_sample_report(self, sample) -> None:
        """ Use this method to reduce values increased by the old result, except for 'processed_on' """
        self._register_multiple_fields_and_values(sample,
                                                  [self._get_status(sample),
                                                   self._get_elapsed_time(sample)],
                                                  increase=False)

    def _register_multiple_fields_and_values(self, sample, fields_and_values: List[Tuple[str, str]], increase=True) -> None:
        for field, value in fields_and_values:
            self._register_field_and_value(sample.file_type, field, value, increase)

    def _register_field_and_value(self, file_type: str, field: str, value: str, increase=True) -> None:
        """ For instance, register_at_field(file_type="flash", field="seconds", value="12")
            register that a flash sample needed 12 seconds to be decompiled"""
        self.redis.hincrby(f'{file_type}:{field}', value, 1 if increase else -1)

    def _flush(self) -> None:
        """ Use this method only for testing or manually wiping the DB. """
        self.redis.flushall()

    # Methods to get information of sample
    def _get_uploaded_on(self, sample) -> Tuple[str, str]:
        return 'uploaded_on', sample.uploaded_on.date().isoformat()

    def _get_size(self, sample) -> Tuple[str, str]:
        """ returns size in kb """
        return 'size', str(int(sample.size/1024))

    def _get_status(self, sample) -> Tuple[str, str]:
        return 'status', str(sample.result.status)

    def _get_processed_on(self, sample) -> Tuple[str, str]:
        return 'processed_on', sample.result.processed_on.date().isoformat()

    def _get_elapsed_time(self, sample) -> Tuple[str, str]:
        """ returns elapsed time in seconds. """
        return 'elapsed_time', str(sample.result.elapsed_time)
