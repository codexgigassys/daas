import logging

from .classifiers import zip_classifier
from .configuration_manager import ConfigurationManager


class ClassifierError(Exception):
    pass


def get_identifier_of_file(binary):
    return 'zip' if zip_classifier(binary) else get_identifier_of_sample(binary)


def get_identifier_of_sample(binary):
    configuration = ConfigurationManager().get_config_for_sample(binary)
    if configuration is not None:  # if there are any classifier (in classifiers.py) that returns True for this binary:
        logging.info('File type detected: %s' % configuration.identifier)
        return configuration.identifier
    else:
        raise ClassifierError('No filter for the given sample')
