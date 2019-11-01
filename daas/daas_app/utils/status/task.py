from enum import Enum


class TaskStatus(Enum):
    # Possible status for redis queue jobs:
    QUEUED = 0
    PROCESSING = 1
    DONE = 2
    FAILED = 3
    # If the user cancels the task:
    CANCELLED = 4
