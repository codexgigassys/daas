from .decompiler import SubprocessBasedDecompiler
# Needed for 'eval':
from .workers import *


class DecompilerCreator:
    def create(self, config):
        self.sample_type = config['sample_type']
        self.decompiler_name = config['decompiler_name']
        if config['requires_library']:
            return self.create_library_based_decompiler(config)
        else:
            return self.create_subprocess_based_decompiler(config)

    def create_subprocess_based_decompiler(self, config):
        decompiler_class = eval(config.get('decompiler_class', "SubprocessBasedDecompiler"))
        nice = config.get('nice', 0)
        timeout = config.get('timeout', 120)
        processes_to_kill = config.get('processes_to_kill', [])
        custom_current_working_directory = config.get('custom_current_working_directory', None)
        return decompiler_class(self.decompiler_name, self.sample_type, nice, timeout,
                                config['decompiler_command'], processes_to_kill,
                                custom_current_working_directory)

    def create_library_based_decompiler(self, config):
        # TODO
        pass
