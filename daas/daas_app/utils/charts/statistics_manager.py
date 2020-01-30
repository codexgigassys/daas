from typing import List, Tuple
import itertools
import datetime
from django.db import models
import logging

from ...utils.configuration_manager import ConfigurationManager
from ..singleton import ThreadSafeSingleton
from .groups import DateCounterGroup, IntegerRangeCounterGroup
from .sample_adapter import SampleAdapter
from .statistics_redis import StatisticsRedis
from ..status import ResultStatus


class StatisticsManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self._redis = StatisticsRedis()

    # Public methods to retrieve statistics
    def get_size_statistics_for_file_type(self, file_type: str) -> IntegerRangeCounterGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='size', logarithm_base=2)

    def get_elapsed_time_statistics_for_file_type(self, file_type: str) -> IntegerRangeCounterGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='elapsed_time', logarithm_base=2)

    def get_sample_count_per_file_type(self) -> List[Tuple[str, int]]:
        return [(file_type, self._redis.get_count_for_file_type(file_type)) for file_type in ConfigurationManager().get_identifiers()]

    def get_total_sample_count(self) -> int:
        return sum([file_type_and_count[1] for file_type_and_count in self.get_sample_count_per_file_type()])

    def get_sample_count_per_status_for_type(self, file_type: str) -> List[Tuple[str, int]]:
        statistics = self._redis.get_statistics_for(file_type=file_type, field='status')
        return [(ResultStatus(int(key)).as_printable_string, int(value)) for key, value in statistics.items()]

    def get_sample_counts_per_upload_date(self, file_type: str) -> DateCounterGroup:
        return self._get_sample_counts_per_date(file_type=file_type, field='uploaded_on')

    def get_sample_counts_per_process_date(self, file_type: str) -> DateCounterGroup:
        return self._get_sample_counts_per_date(file_type=file_type, field='processed_on')

    # Report events to update statistics
    def report_uploaded_sample(self, sample: models.Model) -> None:
        """ Use this method after receiving a new sample. If the sample is not new, you should not use this method. """
        self._register_multiple_fields_and_values(sample, ['uploaded_on', 'size'])
        file_type = sample.file_type if sample.file_type else 'unknown'  # set it as unknown. Useful in testing.
        if file_type == 'unknown':
            logging.warning('File type for {sample=} is unknown.')
        self._redis.register_new_sample_for_type(file_type)

    def report_processed_sample(self, sample: models.Model) -> None:
        """ Use this method after processing or reprocessing a sample. """
        self._register_multiple_fields_and_values(sample, ['status', 'processed_on', 'elapsed_time'])

    def revert_processed_sample_report(self, sample: models.Model) -> None:
        """ Use this method to reduce values increased by the old result, except for 'processed_on' """
        self._register_multiple_fields_and_values(sample, ['status',  'elapsed_time'], increase=False)

    # Other public methods
    def get_minimum_date(self) -> datetime.date:
        values_per_file_type = self._get_all_keys_for_field('uploaded_on') + self._get_all_keys_for_field('processed_on')
        iso_formatted_first_date = min(values_per_file_type) if values_per_file_type else bytes(datetime.date.today().isoformat().encode('utf-8'))
        return datetime.date(*[int(part) for part in iso_formatted_first_date.split(b'-')])

    def flush(self) -> None:
        """ Use this method only for testing or manually wiping the DB. """
        self._redis.flush()

    # Private methods
    def _get_sample_counts_per_date(self, file_type: str, field: str) -> DateCounterGroup:
        statistics = self._redis.get_statistics_for(file_type=file_type, field=field)
        return DateCounterGroup(file_type=file_type,  statistics=statistics)

    def _get_all_keys_for_field(self, field: str) -> List[bytes]:
        """ Returns all keys related to a field, regardless the file type. """
        keys_per_file_type = [self._redis.get_statistics_for(file_type=file_type, field=field).keys() for file_type in
                              ConfigurationManager().get_identifiers()]
        # Flatten the list of lists into a single list
        return list(itertools.chain.from_iterable(keys_per_file_type))

    def _get_maximum_for_integer_field(self, field) -> int:
        values_for_field = [int(value) for value in self._get_all_keys_for_field(field)]
        # Return zero in case there are no values loaded in redis
        return max(values_for_field) if values_for_field else 0

    def _get_statistics_in_ranges_for(self, file_type: str, field: str, logarithm_base: int) -> IntegerRangeCounterGroup:
        statistics = self._redis.get_statistics_for(file_type=file_type, field=field)
        return IntegerRangeCounterGroup(file_type=file_type,
                                        statistics=statistics,
                                        maximum=self._get_maximum_for_integer_field(field),
                                        logarithm_base=logarithm_base)

    def _register_multiple_fields_and_values(self, sample: models.Model, fields: List[str], increase=True) -> None:
        sample = SampleAdapter(sample)
        for field, value in sample.get_fields_and_values(fields):
            self._redis.register_field_and_value(sample.file_type, field, value, increase)
