import subprocess
import logging
import time
import os
DOCUMENT_PATH = ''
EXTRACTION_DIRECTORY = ''


class Worker:
    def __init__(self, sample):
        self.sample = sample
        # We delegate the customizable part of the initialization
        # because in future releases we will want to change part of the initialization
        # on some subclasses.
        self.initialize()

    def initialize(self):
        self.clean()
        self.save_sample()
        self.create_tmpfs_folder()

    def get_name(self):
        return "csharp"

    # ------

    def save_sample(self):
        file_ = open(self.get_tmpfs_file_path(), 'wb')
        file_.write(self.sample)
        file_.close()

    def create_tmpfs_folder(self):
        os.mkdir(self.get_tmpfs_folder_path())

    def get_tmpfs_folder_path(self):
        # All workers use the same path for the same file type because they run on different containers,
        # so race conditions between them are impossible
        return '/tmpfs/%s' % self.get_name()

    def get_tmpfs_file_path(self):
        return '/tmpfs/%s.sample' % self.get_name()

    def process_clean():
        # Sometimes wine processes or xvfb continue running after the subprocess call ends.
        # So we need to kill them to avoid memory leaks
        for regex in [r'.+\.exe.*', r'.*wine.*', r'.*[xX]vfb.*']:
            subprocess.call(['pkill', regex])

    def folder_clean(self):
        """ todo """
        pass

    def decode_output(self, output):
        try:
            return output.decode("utf-8").strip()
        except UnicodeDecodeError:
            return unicode(output, errors="replace").strip()

    def nice(self, value):
        return ['nice', '-n', value]

    def timeout(self, seconds):
        return ['timeout', '-k', '30', str(seconds)]

    def command(self, command, nice=True, nice_value=2, timeout=True, timeout_value=1000):
        if timeout:
            command = self.timeout(timeout_value) + command
        if nice:
            command = self.nice(nice_value) + command
        return command


class CSharpWorker(Worker):
    # TODO: some of this logic should be on the superclass.
    def decompile(self):
        csharp_command = ["wine", "/just_decompile/ConsoleRunner.exe", "/target:" + DOCUMENT_PATH,
                          "/out:" + EXTRACTION_DIRECTORY]
        full_command = self.command(csharp_command)
        logging.debug('Running command: %s' % full_command)
        start = time.time()
        try:
            start = time.time()
            output = subprocess.check_output(full_command, stderr=subprocess.STDOUT)
            # Details and info for statistics
            elapsed_time = int(time.time() - start)
            exit_status = 0  # The decompiler didn't crash
            exception_info = {}
        except subprocess.CalledProcessError as e:
            # Details and info for statistics
            elapsed_time = int(time.time() - start)
            exit_status = e.returncode
            output = e.output
            exception_info = {'message': e.message,
                              'command': e.cmd,
                              'arguments': e.args}
            logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (elapsed_time, TIMEOUT))
            logging.debug('Exception info: %s' % exception_info)
            # Exception handling
            if exit_status == 124:  # exit status is 124 when the timeout is reached.
                logging.debug('Process timed out.')
            else:
                logging.debug('Unknown exit status code: %s.' % exit_status)
        info_for_statistics = {'timeout': TIMEOUT,
                               'elapsed_time': elapsed_time + 1,
                               'exit_status': exit_status,
                               'timed_out': exit_status == 124,
                               'exception_info': exception_info,
                               'output': self.decode_output(output),
                               'errors': self.get_errors(output)}
        return info_for_statistics

    def get_errors(self, output):
        lines = output.replace('\r', '').split('\n')
        return [fname.split(' ')[1][fname.split(' ')[1].find('.') + 1:] for fname in lines if
                fname.find(' ... error generating.') > 0]


