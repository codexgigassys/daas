from .decompiler import CSharpDecompiler

csharp = {'sample_type': 'C#',
          'decompiler_name': 'Just Decompile',
          'requires_library': False,
          'decompiler_class': CSharpDecompiler,
          'processes_to_kill': [r'.+\.exe.*'],
          'nice': 2,
          'timeout': 120,
          'decompiler_command': ["wine", "/just_decompile/ConsoleRunner.exe",
                                 "/target: @sample_path",
                                 "/out: @extraction_path"]}

flash = {'sample_type': 'Flash',
         'decompiler_name': 'FFDec',
         'requires_library': False,
         'timeout': 720,
         'decompiler_command': ['ffdec', '-onerror', 'ignore', '-timeout', '600', '-exportTimeout',
                                '600', '-exportFileTimeout', '600', '-export', 'all',
                                '@extraction_path', '@sample_path']}
