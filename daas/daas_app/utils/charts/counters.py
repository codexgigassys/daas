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


class DateCounter:
    def __init__(self, iso_formatted_date: str) -> None:
        self.iso_formatted_date = iso_formatted_date
        self.count = 0

    def value_in_range(self, iso_formatted_date: bytes) -> bool:
        return bytes(self.iso_formatted_date.encode('utf-8')) == iso_formatted_date

    @property
    def caption(self) -> str:
        """ To maintain polymorphism across this class and Range class."""
        return self.iso_formatted_date
