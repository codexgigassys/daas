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
          'version': 2}

flash = {'sample_type': 'Flash',
         'identifier': 'flash',
         'decompiler_name': 'FFDec',
         'requires_library': False,
         'timeout': 720,
         'decompiler_command': "ffdec -onerror ignore -timeout 600 -exportTimeout 600 \
                                -exportFileTimeout 600 -export all \
                                @extraction_path @sample_path",
         'version': 1}


java = {'sample_type': 'Java',
        'identifier': 'java',
        'decompiler_name': 'jd-cli',
        'requires_library': False,
        'nice': 2,
        'timeout': 180,
        'decompiler_command': 'java -jar /jd-cli/jd-cli.jar @sample_path -od @extraction_path',
        'version': 1}


configs = [csharp, flash, java]
