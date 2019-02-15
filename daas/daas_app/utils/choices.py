from .configuration_manager import ConfigurationManager
from .redis_status import FAILED, CANCELLED, QUEUED, PROCESSING, DONE


def sorted_choices(unsorted_choices):
    unsorted_choices.sort(key=lambda x: x[1])
    return unsorted_choices


FILE_TYPE_CHOICES = sorted_choices([(file_type, ConfigurationManager().get_configuration(file_type).sample_type)
                                    for file_type in ConfigurationManager().get_identifiers()] + [('', 'All')])

REDIS_JOB_CHOICES = sorted_choices([(QUEUED, QUEUED), (PROCESSING, PROCESSING), (DONE, DONE), (FAILED, FAILED),
                                    (CANCELLED, CANCELLED)] + [('', 'All')])
