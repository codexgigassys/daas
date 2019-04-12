import logging

from .classifiers import zip_classifier
from .configuration_manager import ConfigurationManager


class ClassifierError(Exception):
    pass


def get_identifier_of_file(binary):
    if zip_classifier(binary):
        return 'zip'
    else:
        configuration = ConfigurationManager().get_config_for_file(binary)
        if configuration is not None:  # if there is any classifier (in classifiers.py) that returns True for this binary:
            logging.info('File type detected: %s' % configuration.identifier)
            return configuration.identifier
        else:
            raise ClassifierError('No filter for the given sample')
