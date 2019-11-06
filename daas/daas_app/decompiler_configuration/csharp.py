csharp = {'sample_type': 'C#',
          'identifier': 'pe',
          'decompiler_name': 'Just Decompile',
          'requires_library': False,
          'decompiler_class': "CSharpDecompiler",
          'processes_to_kill': [r'.+\.exe.*'],
          'nice': 2,
          'timeout': 120,
          'decompiler_command': "wine /just_decompile/ConsoleRunner.exe \
                                '/target: @sample_path' \
                                '/out: @extraction_path'",
          'source_compression_algorithm': 'xztar',
          'version': 2}
