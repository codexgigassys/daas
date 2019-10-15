import sys
import shutil
import time


def compress(name):
    for folder in ['flash', 'csharp', 'java']:
        for format in ['zip', 'gztar', 'bztar', 'xztar']:
            start = time.process_time()
            shutil.make_archive(f'/tmp/aux/{folder}_{name}', format, f'/tmp/aux/{folder}/')
            print(f'{folder}_{name} ({format}): {time.process_time() - start}')
    print('\n')


compress(sys.argv[1])
