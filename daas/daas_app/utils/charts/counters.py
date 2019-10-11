class IntegerRangeCounter:
    def __init__(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum
        self.count = 0

    def value_in_range(self, value: bytes) -> bool:
        return self._minimum <= int(value) <= self._maximum

    def increment_count_by(self, count: int) -> None:
        self.count += count

    @property
    def caption(self) -> str:
        return f'{self._minimum} - {self._maximum}'


class DateCounter(IntegerRangeCounter):
    def __init__(self, iso_formatted_date: str) -> None:
        self._iso_formatted_date = iso_formatted_date
        self.count = 0

    def value_in_range(self, iso_formatted_date: bytes) -> bool:
        return bytes(self._iso_formatted_date.encode('utf-8')) == iso_formatted_date

    @property
    def caption(self) -> str:
        """ To maintain polymorphism across this class and Range class
            without losing expresiveness within the class. """
        return self._iso_formatted_date
