from .configuration_manager import ConfigurationManager


def sorted_choices(unsorted_choices):
    unsorted_choices.sort(key=lambda x: x[1])
    return unsorted_choices


FILE_TYPE_CHOICES = sorted_choices([(file_type, ConfigurationManager().get_configuration(file_type).sample_type)
                                    for file_type in ConfigurationManager().get_identifiers()] + [('', 'All')])
