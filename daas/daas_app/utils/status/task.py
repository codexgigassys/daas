from enum import Enum


class TaskStatus(Enum):
    QUEUED = 0
    CANCELLED = 1
    PROCESSING = 2
    DONE = 3
    FAILED = 4  # If the user cancels the task
    NO_TASK = 5
