from .singleton import Singleton
from ..decompilers.decompiler_config import configs
# Needed for 'eval':
from .classifiers import *


class Configuration:
    """ wrapper of configuration dictionary"""
    def __init__(self, dictionary):
        self.dictionary = dictionary

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
    def classifier(self):
        """ returns the classifier function for this configuration as a function """
        return eval('%s_classifier' % self.identifier)

    @property
    def timeout(self):
        return self.dictionary['timeout']

    @property
    def version(self):
        return self.dictionary.get('version', 0)

    def is_valid_for(self, binary):
        return self.classifier(binary)

    def as_dictionary(self):
        return self.dictionary


class ConfigurationManager(metaclass=Singleton):
    def __init__(self):
        self.configurations = {}
        for configuration_dictionary in configs:
            configuration = Configuration(configuration_dictionary)
            self.configurations[configuration.identifier] = configuration

    def get_identifiers(self):
        return list(self.configurations.keys())

    def get_configurations(self):
        return list(self.configurations.values())

    def get_configuration(self, identifier):
        return self.configurations.get(identifier, None)

    def get_config_for_sample(self, binary):
        """ returns the configuration object of the first configuration whose filter
            matches the given if possible, otherwise returns None """
        for configuration in self.get_configurations():
            if configuration.is_valid_for(binary):
                return configuration
