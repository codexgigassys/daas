from django_redis import get_redis_connection
from typing import SupportsInt, List, Tuple, Dict
import itertools
import math
import datetime

from daas_app.utils.configuration_manager import ConfigurationManager
from .singleton import ThreadSafeSingleton


class IntegerRangeCounter:
    def __init__(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum
        self.count = 0

    def value_in_range(self, value: bytes) -> bool:
        return self.minimum <= int(value) <= self.maximum

    def increment_count_by(self, count: int) -> None:
        self.count += count

    @property
    def caption(self) -> str:
        return f'{self.minimum} - {self.maximum}'


class IntegerRangeCounterGroup:
    def __init__(self, file_type: str, statistics: Dict[bytes, SupportsInt], maximum: int, logarithm_base: int) -> None:
        self.ranges = self._generate_ranges(maximum, logarithm_base)
        self.file_type = file_type
        self._load_statistics(statistics)

    def _load_statistics(self, statistics: Dict[bytes, SupportsInt]) -> None:
        for value, count in statistics.items():
            self._add_count_to_corresponding_range(value, count)

    def _generate_ranges(self, maximum: int, logarithm_base: int) -> List[IntegerRangeCounter]:
        """ Generate ranges for charts using logarithmic scale with base <logarithm_base>.
            It will generate ranges until <maximum> is reached"""
        # Transform the maximum to logarithmic scale
        maximum = math.ceil(math.log(maximum if maximum >= 1 else 1, logarithm_base))
        # Generate ranges
        ranges = []
        for i in range(maximum):
            range_minimum = logarithm_base**i if i > 0 else 0  # To start the first range (i=0) at 0 instead of 1
            range_maximum = logarithm_base**(i+1) - 1
            ranges.append(IntegerRangeCounter(range_minimum, range_maximum))
        return ranges

    def _add_count_to_corresponding_range(self, value: bytes, count: bytes) -> None:
        for range in self.ranges:
            if range.value_in_range(value):
                range.increment_count_by(int(count))

    @property
    def captions(self) -> List[str]:
        return [range.caption for range in self.ranges]

    @property
    def counts(self) -> List[int]:
        return [range.count for range in self.ranges]


class DateCounter:
    def __init__(self, iso_formatted_date: str) -> None:
        self.iso_formatted_date = iso_formatted_date
        self.count = 0

    def value_in_range(self, iso_formatted_date: bytes) -> bool:
        return self.iso_formatted_date == str(iso_formatted_date)

    @property
    def caption(self) -> str:
        """ To maintain polymorphism across this class and Range class."""
        return self.iso_formatted_date


class DateCounterGroup(IntegerRangeCounterGroup):
    def __init__(self, file_type: str, statistics: Dict[bytes, SupportsInt]) -> None:
        self.ranges = self._generate_ranges()
        self.file_type = file_type
        self._load_statistics(statistics)

    def _load_statistics(self, statistics: Dict[bytes, SupportsInt]) -> None:
        for value, count in statistics.items():
            self._add_count_to_corresponding_range(str(value), int(count))

    def _generate_ranges(self) -> List[DateCounter]:
        ranges = []
        date = StatisticsManager().get_minimum_date()
        while date <= datetime.date.today():
            ranges.append(DateCounter(date.isoformat()))
            date += datetime.timedelta(days=1)
        return ranges


class StatisticsManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self.redis = get_redis_connection("default")

    # Public methods to retrieve statistics
    def get_size_statistics_for_file_type(self, file_type) -> IntegerRangeCounterGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='size', logarithm_base=2)

    def get_elapsed_time_statistics_for_file_type(self, file_type) -> IntegerRangeCounterGroup:
        return self._get_statistics_in_ranges_for(file_type=file_type, field='elapsed_time', logarithm_base=2)

    def get_sample_count_per_file_type(self) -> List[Tuple[str, int]]:
        return [(file_type, self._get_count_for_file_type(file_type)) for file_type in ConfigurationManager().get_identifiers()]

    def get_sample_count_per_upload_date(self, file_type) -> DateCounterGroup:
        statistics = self._get_statistics_for(file_type=file_type, field='uploaded_on')
        return DateCounterGroup(file_type=file_type,  statistics=statistics)

    # Report events to update statistics
    def report_uploaded_sample(self, sample) -> None:
        """ Use this method after receiving a new sample. If the sample is not new, you should not use this method. """
        self._register_multiple_fields_and_values(sample, [self._get_uploaded_on(sample),
                                                           self._get_size(sample)])
        self.redis.incrby(sample.file_type, 1)

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

    # Other public methods
    def get_minimum_date(self) -> datetime.date:
        """ It looks on uploaded_on because it's not possible to have a processed_on previous to the first
            upload date. """
        values_per_file_type = self._get_all_keys_for_field('uploaded_on')
        iso_formatted_first_date = min(values_per_file_type) if values_per_file_type else datetime.date.today().isoformat()
        return datetime.date(*[int(part) for part in iso_formatted_first_date.split(b'-')])

    # Private methods
    def _get_count_for_file_type(self, file_type: str) -> int:
        count_at_redis = self.redis.get(file_type)
        return int(count_at_redis) if count_at_redis else 0

    def _get_statistics_for(self, file_type: str, field: str) -> Dict[bytes, SupportsInt]:
        return self.redis.hgetall(f'{file_type}:{field}')

    def _get_all_keys_for_field(self, field: str) -> List[bytes]:
        """ Returns all keys related to a field, regardless the file type. """
        keys_per_file_type = [self._get_statistics_for(file_type=file_type, field=field).keys() for file_type in
                              ConfigurationManager().get_identifiers()]
        # Flatten the list of lists into a single list
        return list(itertools.chain.from_iterable(keys_per_file_type))

    def _get_maximum_for_integer_field(self, field) -> int:
        values_for_field = [int(value) for value in self._get_all_keys_for_field(field)]
        # Returns zero in case there are no values loaded in redis
        return max(values_for_field) if values_for_field else 0

    def _get_statistics_in_ranges_for(self, file_type: str, field: str, logarithm_base: int) -> IntegerRangeCounterGroup:
        statistics = self._get_statistics_for(file_type=file_type, field=field)
        return IntegerRangeCounterGroup(file_type=file_type,
                                        statistics=statistics,
                                        maximum=self._get_maximum_for_integer_field(field),
                                        logarithm_base=logarithm_base)

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

    # Private methods to get information of a sample
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
