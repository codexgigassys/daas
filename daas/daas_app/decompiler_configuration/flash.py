flash = {'sample_type': 'Flash',
         'identifier': 'flash',
         'decompiler_name': 'FFDec',
         'requires_library': False,
         'timeout': 600,
         'decompiler_command': "ffdec \
                                -onerror ignore \
                                -timeout 60  \
                                -exportTimeout 600  \
                                -exportFileTimeout 120  \
                                -export script,image,binaryData,text \
                                @extraction_path \
                                @sample_path",
         'source_compression_algorithm': 'bztar',
         'version': 2}
