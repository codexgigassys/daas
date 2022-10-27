from typing import Dict, Any
from .decompiler import SubprocessBasedDecompiler

# Needed for 'eval':
from .decompiler import *
from .csharp_decompiler import CSharpDecompiler
from .apk_decompiler import APKDecompiler


class DecompilerFactory:
    def create(self, config):
        self.decompiler_name = config['decompiler_name']
        self.sample_type = config['sample_type']
        self.extension = config.get('extension', 'sample')
        self.version = config.get('version', 0)
        self.source_compression_algorithm = config.get('source_compression_algorithm', 'xztar')
        if config['requires_library']:
            return self.create_library_based_decompiler(config)
        else:
            return self.create_subprocess_based_decompiler(config)

    def create_subprocess_based_decompiler(self, config: Dict[str, Any]) -> SubprocessBasedDecompiler:
        nice = config.get('nice', 0)
        timeout = config.get('timeout', 120)
        creates_windows = config.get('creates_windows', False)
        processes_to_kill = config.get('processes_to_kill', [])
        custom_current_working_directory = config.get('custom_current_working_directory', None)
        decompiler_class = eval(config.get('decompiler_class', 'SubprocessBasedDecompiler'))
        return decompiler_class(self.decompiler_name, self.sample_type, self.extension, self.source_compression_algorithm,
                                nice, timeout,
                                creates_windows, config['decompiler_command'], processes_to_kill,
                                custom_current_working_directory, self.version)
