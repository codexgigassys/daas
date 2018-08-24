import subprocess
import logging
subprocess_function = "subprocess.check_output(@command, stderr=subprocess.STDOUT)"
TIMEOUT = 1000  # Seconds
DOCUMENT_PATH = ''
EXTRACTION_DIRECTORY= ''


# Example:
# timedout_subprocess_eval('subprocess.check_output(@command, stderr=subprocess.STDOUT)',
#                          command = ["echo", "i\'m a command!"])
def timedout_subprocess_eval(self, subprocess_function_as_string, bash_command):
    nice_command = ['nice', '-n', '2']
    timeout_command = ['timeout', '-k', '30', str(TIMEOUT)]
    csharp_command = ["wine", "/just_decompile/ConsoleRunner.exe", "/target:" + DOCUMENT_PATH, "/out:" + EXTRACTION_DIRECTORY]
    full_command = nice_command + timeout_command + csharp_command
    info_for_statistics = {'timeout': TIMEOUT}
    logging.debug('Running command: %s' % full_command)
    try:
        start = time.time()
        output = eval(full_subprocess_function)
        elapsed_time = time.time() - start
        self.info_for_statistics['elapsed_time'] = int(elapsed_time) + 1
        self.info_for_statistics['exit_status'] = 0
    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start
        info_for_statistics['elapsed_time'] = int(elapsed_time) + 1
        info_for_statistics['exit_status'] = e.returncode
        logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (int(elapsed_time), int(self.getTimeout())))
        logging.debug('Exception info: %s' % {'return_code': e.returncode, 'output': e.output, 'message': e.message, 'command': e.cmd, 'arguments': e.args})
        if e.returncode == 124:
            logging.debug('Process timed out. Raising exception...')
        else:
            logging.debug('Strange status code: %s. Raising exception...' % e.returncode)
        raise e
    return self.decode_output(output)