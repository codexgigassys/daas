import subprocess
import logging
import time
subprocess_function = "subprocess.check_output(@command, stderr=subprocess.STDOUT)"
TIMEOUT = 1000  # Seconds
DOCUMENT_PATH = ''
EXTRACTION_DIRECTORY = ''


def csharp_decompile():
    nice_command = ['nice', '-n', '2']
    timeout_command = ['timeout', '-k', '30', str(TIMEOUT)]
    csharp_command = ["wine", "/just_decompile/ConsoleRunner.exe", "/target:" + DOCUMENT_PATH, "/out:" + EXTRACTION_DIRECTORY]
    full_command = nice_command + timeout_command + csharp_command
    logging.debug('Running command: %s' % full_command)
    start = time.time()
    try:
        start = time.time()
        output = subprocess.check_output(full_command, stderr=subprocess.STDOUT)
        # Details and info for statistics
        elapsed_time = time.time() - start
        exit_status = 0  # The decompiler didn't crash
        exception_info = {}
    except subprocess.CalledProcessError as e:
        # Details and info for statistics
        elapsed_time = time.time() - start
        exit_status = e.returncode
        output = e.output
        exception_info = {'message': e.message,
                          'command': e.cmd,
                          'arguments': e.args}
        logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (int(elapsed_time), TIMEOUT))
        logging.debug('Exception info: %s' % exception_info)
        # Exception handling
        if exit_status == 124:  # exit status is 124 when the timeout is reached.
            logging.debug('Process timed out.')
        else:
            logging.debug('Unknown exit status code: %s.' % exit_status)
    info_for_statistics = {'timeout': TIMEOUT,
                           'elapsed_time': int(elapsed_time) + 1,
                           'exit_status': exit_status,
                           'timed_out': exit_status == 124,
                           'exception_info': exception_info,
                           'output': decode_output(output)}
    return info_for_statistics


def errors(output):
    lines = output.replace('\r', '').split('\n')
    return [fname.split(' ')[1][fname.split(' ')[1].find('.') + 1:] for fname in lines if
            fname.find(' ... error generating.') > 0]


def decode_output(output):
    try:
        return output.decode("utf-8").strip()
    except UnicodeDecodeError:
        return unicode(output, errors="replace").strip()


def process_clean():
    # Sometimes wine processes or xvfb continue running after the subprocess call ends.
    # So we need to kill them to avoid memory leaks
    for regex in [r'.+\.exe.*', r'.*wine.*', r'.*[xX]vfb.*']:
        subprocess.call(['pkill', regex])
