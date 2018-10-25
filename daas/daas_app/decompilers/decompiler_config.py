from .decompiler import CSharpDecompiler

csharp = {'sample_type': 'C#',
          'decompiler_name': 'Just Decompile',
          'requires_library': False,
          'decompiler_class': CSharpDecompiler,
          'processes_to_kill': [r'.+\.exe.*'],
          'nice': 2,
          'decompiler_command': ["wine", "/just_decompile/ConsoleRunner.exe",
                                 "/target: @sample_path",
                                 "/out: @extraction_path"]}
