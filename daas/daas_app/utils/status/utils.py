from enum import Enum as DefaultEnum


class Enum(DefaultEnum):
    @property
    def as_printable_string(self) -> str:
        return f'{self.name[0]}{self.name[1:].lower()}'
