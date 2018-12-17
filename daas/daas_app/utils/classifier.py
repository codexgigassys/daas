from . import zip_distributor
from .configuration_manager import ConfigurationManager


class ClassifierError(Exception):
    pass


def classify(binary):
    if zip_distributor.is_zip(binary):
        zip_distributor.upload_files_of(binary)
        identifier = 'zip'
    else:
        identifier = get_identifier_of(binary)
    return identifier


def get_identifier_of(binary):
    configuration = ConfigurationManager().get_config_for_sample(binary)
    if configuration is not None:  # if there are any classifier (in classifiers.py) that returns True for this binary:
        return configuration.identifier
    else:
        raise ClassifierError('No filter for the given sample')
