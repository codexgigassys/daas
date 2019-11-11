java = {'sample_type': 'Java',
        'extension': 'jar',
        'identifier': 'java',
        'decompiler_name': 'crf',
        'requires_library': False,
        'nice': 2,
        'timeout': 180,
        'decompiler_command': "java -jar /cfr/cfr.jar \
                               @sample_path \
                               --outputdir @extraction_path",
        'source_compression_algorithm': 'bztar',
        'version': 2}
