from typing import SupportsInt, List, Dict
import math
import datetime
import bottleneck

from .counters import IntegerRangeCounter, DateCounter


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


class DateCounterGroup(IntegerRangeCounterGroup):
    def __init__(self, file_type: str, statistics: Dict[bytes, SupportsInt]) -> None:
        self.ranges = self._generate_ranges()
        self.file_type = file_type
        self.sma_window = 7
        self._load_statistics(statistics)

    def _generate_ranges(self) -> List[DateCounter]:
        # Use a dynamic import to avoid recursive imports
        from .statistics_manager import StatisticsManager
        ranges = []
        date = StatisticsManager().get_minimum_date()
        while date <= datetime.date.today():
            ranges.append(DateCounter(date.isoformat()))
            date += datetime.timedelta(days=1)
        return ranges

    @property
    def simple_moving_average(self) -> List[int]:
        """ Calculates the simple moving average (SMA). """
        return [round(move_mean_value, 1) for move_mean_value in
                bottleneck.move_mean(self.counts, window=self.sma_window, min_count=1)]

    @property
    def simple_moving_average_legend(self) -> str:
        return f'{self.file_type} SMA ({self.sma_window} days)'
