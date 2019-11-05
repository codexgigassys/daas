from .utils import Enum


class SampleStatus(Enum):
    QUEUED = 0
    CANCELLED = 1
    PROCESSING = 2
    FAILED = 3
    TIMED_OUT = 4
    DONE = 5
    INVALID = 6  # when task and result status does not match in any logical way.
