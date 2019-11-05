from .utils import Enum


class ResultStatus(Enum):
    SUCCESS = 0
    TIMED_OUT = 1
    FAILED = 2
    NO_RESULT = 3  # to use when there are no results
