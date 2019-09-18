import sys
import shutil
import time


def compress(name):
    for folder in ['flash', 'csharp', 'java']:
        for format in ['zip', 'gztar', 'bztar', 'xztar']:
        start = time.process_time()
            shutil.make_archive('/tmp/aux/%s_%s' % (folder, name), format, '/tmp/aux/%s/' % folder)
            print('%s_%s (%s): %s' % (folder, name, format, time.process_time() - start))
    print('\n')


compress(sys.argv[1])
