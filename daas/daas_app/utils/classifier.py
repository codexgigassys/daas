from .redis_manager import RedisManager
from . import zip_distributor
from .configuration_manager import ConfigurationManager


class ClassifierError(Exception):
    pass


def classify(binary):
    if zip_distributor.is_zip(binary):
        zip_distributor.upload_files_of(binary)
        identifier = 'zip'
        job_id = None
    else:
        identifier, job_id = send_to_queue(binary)
    return identifier, job_id


def send_to_queue(binary):
    configuration = ConfigurationManager().get_config_for_sample(binary)
    if configuration is not None:  # if there are any classifier (in classifiers.py) that returns True for this binary:
        return RedisManager().submit_sample(binary, configuration)
    else:
        raise ClassifierError('No filter for the given sample')
