from enum import Enum


class ResultStatus(Enum):
    SUCCESS = 0
    TIMED_OUT = 1
    FAILED = 2
