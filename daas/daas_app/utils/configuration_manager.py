from .singleton import Singleton
from ..decompilers.decompiler_config import configs
# Needed for 'eval':
from .sample_classifiers.classifiers import *


class Configuration:
    """ wrapper of configuration dictionary"""
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def get_identifier(self):
        return self.dictionary['identifier']

    def get_sample_type(self):
        return self.dictionary['sample_type']

    def get_queue_name(self):
        return '%s_queue' % self.get_identifier()

    def get_classifier(self):
        return eval('%s_classifier' % self.get_identifier())

    def is_valid_for(self, sample):
        return self.get_classifier()(sample)

    def as_dictionary(self):
        return self.dictionary

    def get_timeout(self):
        return self.dictionary['timeout']

    def get_version(self):
        return self.dictionary.get('version', 0)


class ConfigurationManager(metaclass=Singleton):
    def __init__(self):
        self.configurations = {}
        for configuration_dictionary in configs:
            configuration = Configuration(configuration_dictionary)
            self.configurations[configuration.get_identifier()] = configuration

    def get_identifiers(self):
        return list(self.configurations.keys())

    def get_configurations(self):
        return list(self.configurations.values())

    def get_configuration(self, identifier):
        return self.configurations.get(identifier, None)

    def get_config_for_sample(self, sample):
        for configuration in self.get_configurations():
            if configuration.is_valid_for(sample):
                return configuration
