from typing import List, Tuple

from .configuration_manager import ConfigurationManager
from .status import TaskStatus


def sorted_choices(unsorted_choices: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    unsorted_choices.sort(key=lambda x: x[1])
    return unsorted_choices


FILE_TYPE_CHOICES = sorted_choices([(file_type, ConfigurationManager().get_configuration(file_type).sample_type)
                                    for file_type in ConfigurationManager().get_identifiers()] + [('', 'All')])

REDIS_JOB_CHOICES = sorted_choices([(choice.value,
                                     choice.as_printable_string) for choice in list(TaskStatus)
                                    if choice != TaskStatus.NO_TASK] + [('', 'All')])
