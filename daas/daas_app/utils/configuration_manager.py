from typing import List

from .singleton import Singleton
from ..decompiler_configuration import configurations
from django.conf import settings


class Configuration:
    """ wrapper of configuration dictionary"""
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def _increase_timeout_on_testing(self):
        self.dictionary['timeout'] = self.dictionary['timeout'] * settings.DECOMPILER_TIMEOUT_MULTIPLIER

    @property
    def identifier(self):
        return self.dictionary['identifier']

    @property
    def sample_type(self):
        return self.dictionary['sample_type']

    @property
    def queue_name(self):
        return '%s_queue' % self.identifier

    @property
    def timeout(self):
        return self.dictionary['timeout']

    @property
    def version(self):
        return self.dictionary.get('version', 0)

    def is_valid_for_sample(self, sample):
        return self.identifier == sample.file_type

    def as_dictionary(self):
        return self.dictionary


class ConfigurationManager(metaclass=Singleton):
    def __init__(self):
        self.configurations = {}
        for configuration_dictionary in configurations:
            configuration = Configuration(configuration_dictionary)
            self.configurations[configuration.identifier] = configuration

    def get_identifiers(self) -> List[str]:
        return list(self.configurations.keys())

    def get_configurations(self):
        return list(self.configurations.values())

    def get_configuration(self, identifier):
        return self.configurations.get(identifier, None)

    def get_config_for_sample(self, sample):
        """ returns the configuration object of the first configuration whose filter
            matches the given if possible, otherwise returns None """
        for configuration in self.get_configurations():
            if configuration.is_valid_for_sample(sample):
                return configuration
