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
        exception_info = {'output': e.output,
                          'message': e.message,
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
                           'exception_info': exception_info}
    return decode_output(output), info_for_statistics


def decode_output(output):
    """ TODO """
    return output
