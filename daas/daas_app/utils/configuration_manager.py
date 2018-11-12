from .singleton import Singleton
from ..decompilers.decompiler_config import configs
# Needed for 'eval':
from ..decompilers.filters import *


class ConfigurationManager(metaclass=Singleton):
    def __init__(self):
        self.configs = {}
        for config in configs:
            self.configs[config['identifier']] = config

    def get_sample_type(self, identifier):
        return self.configs[identifier]['sample_type']

    def get_queue_name(self, identifier):
        return '%s_queue' % identifier

    def get_identifiers(self):
        return list(self.configs.keys())

    def get_filter(self, identifier):
        return eval('%s_filter' % identifier)

    def fullfils_filter_of(self, sample, identifier):
        return self.get_filter(identifier)(sample)

    def get_configuration(self, identifier):
        return self.configs[identifier]

    def get_config_for_sample(self, sample):
        for identifier in self.get_identifiers():
            if self.fullfils_filter_of(sample, identifier):
                return self.get_configuration(identifier)
