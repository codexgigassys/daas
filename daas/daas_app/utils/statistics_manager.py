from django_redis import get_redis_connection
from typing import SupportsBytes, List, Tuple, Dict
import itertools
import math

from daas_app.utils.configuration_manager import ConfigurationManager
from .singleton import ThreadSafeSingleton


class Range:
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        self.count = 0

    def value_in_range(self, value: int) -> bool:
        return self.minimum <= value <= self.maximum

    def increment_count_by(self, count: int) -> None:
        self.count += count

    @property
    def caption(self) -> str:
        return f'{self.minimum} - {self.maximum}'


class RangeGroup:
    def __init__(self, file_type: str, statistics: Dict[bytes, bytes], maximum: int, logarithm_base: int):
        self.ranges = self._generate_ranges(maximum, logarithm_base)
        self.file_type = file_type
        self._load_statistics(statistics)

    def _load_statistics(self, statistics: Dict[bytes, bytes]) -> None:
        for value, count in statistics.items():
            self._add_count_to_corresponding_range(int(value), int(count))

    def _generate_ranges(self, maximum: int, logarithm_base: int) -> List[Range]:
        """ Generate ranges for charts using logarithmic scale with base <logarithm_base>.
            It will generate ranges until <maximum> is reached"""
        maximum = math.ceil(math.log2(maximum))  # Transform the maximum to logarithmic scale.
        ranges = []
        for i in range(maximum):
            range_minimum = logarithm_base**i if i > 0 else 0  # To start the first range (i=0) at 0 instead of 1
            range_maximum = logarithm_base**(i+1) - 1
            ranges.append(Range(range_minimum, range_maximum))
        return ranges

    def _add_count_to_corresponding_range(self, value: int, count: int) -> None:
        for range in self.ranges:
            if range.value_in_range(value):
                range.increment_count_by(count)

    @property
    def captions(self) -> List[str]:
        return [range.caption for range in self.ranges]

    @property
    def counts(self) -> List[int]:
        return [range.count if range.count > 0 else None for range in self.ranges]


class StatisticsManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self.redis = get_redis_connection("default")

    def _get_statistics_for(self, file_type: str, field: str):
        return self.redis.hgetall(f'{file_type}:{field}')

    def _get_maximum_for_field(self, field):
        values_per_file_type = [self._get_statistics_for(file_type, field).keys() for file_type in ConfigurationManager().get_identifiers()]
        flattened_values = [int(value) for value in list(itertools.chain.from_iterable(values_per_file_type))]
        return max(flattened_values + [0])

    def _get_statistics_in_ranges_for(self, file_type: str, field: str, logarithm_base: int) -> RangeGroup:
        statistics = self._get_statistics_for(file_type=file_type, field=field)
        return RangeGroup(file_type=file_type, statistics=statistics, maximum=self._get_maximum_for_field(field), logarithm_base=logarithm_base)

    def get_size_statistics_for_file_type(self, file_type) -> RangeGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='size', logarithm_base=2)

    def get_elapsed_time_statistics(self, file_type) -> RangeGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='elapsed_time', logarithm_base=2)

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
