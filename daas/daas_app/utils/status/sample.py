from enum import Enum


class SampleStatus(Enum):
    QUEUED = 0
    CANCELLED = 1
    PROCESSING = 2
    FAILED = 3
    TIMED_OUT = 4
    DONE = 5
    INVALID = 6  # when task and result status does not match in any logical way.

    @property
    def as_printable_string(self) -> str:
        return f'{self.name[0]}{self.name[1:].lower()}'
