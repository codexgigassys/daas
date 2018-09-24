import subprocess
import logging
import time
import os
from .utils import remove_file, remove_directory
import requests
import hashlib


class Worker:
    def __init__(self, sample):
        self.sample = sample
        self.sha1 = hashlib.sha1(sample).hexdigest()
        # We delegate the customizable part of the initialization
        # because in future releases we will want to change part of the initialization
        # on some subclasses.
        self.add_nice = True
        self.nice_value = 2
        self.add_timeout = True
        self.timeout_value = 120  # seconds
        self.name = "unnamed plugin. You should change this value on subclasses!"
        self.decompiler_command = ["echo", "command not defined!"]
        self.initialize()

    def initialize(self):
        self.set_attributes()
        self.clean()
        self.save_sample()
        self.create_tmpfs_folder()

    def set_attributes(self):
        """ This method should be used as an elegant way to modify default values
        of attributes on subclasses if needed"""
        pass

    def save_sample(self):
        file_ = open(self.get_tmpfs_file_path(), 'wb')
        file_.write(self.sample)
        file_.close()

    def create_tmpfs_folder(self):
        os.mkdir(self.get_tmpfs_folder_path())

    def get_tmpfs_folder_path(self):
        # All workers use the same path for the same file type because they run on different containers,
        # so race conditions between them are impossible
        return '/tmpfs/%s' % self.name

    def get_tmpfs_file_path(self):
        return '/tmpfs/%s.sample' % self.name

    def clean(self):
        remove_file(self.get_tmpfs_file_path())
        remove_directory(self.get_tmpfs_folder_path())

    def decode_output(self, output):
        try:
            return output.decode("utf-8").strip()
        except UnicodeDecodeError:
            return unicode(output, errors="replace").strip()

    def process(self):
        start = time.time()
        try:
            start = time.time()
            output = self.decompile()
            # Details and info for statistics
            elapsed_time = int(time.time() - start)
            exit_status = 0  # The decompiler didn't crash
            exception_info = {}
        except subprocess.CalledProcessError as e:
            # Details and info for statistics
            elapsed_time = int(time.time() - start)
            exit_status = e.returncode
            output = e.output
            logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (elapsed_time, self.timeout_value))
            # Exception handling
            if exit_status == 124:  # exit status is 124 when the timeout is reached.
                logging.debug('Process timed out.')
            else:
                logging.debug('Unknown exit status code: %s.' % exit_status)
        info_for_statistics = {'sha1': self.sha1,
                               'timeout': self.timeout_value,
                               'elapsed_time': elapsed_time + 1,
                               'exit_status': exit_status,
                               'timed_out': exit_status == 124,
                               'output': self.decode_output(output),
                               'errors': self.get_errors(output)}
        return info_for_statistics

    def get_errors(self, output):
        lines = str(output).replace('\r', '').split('\n')
        return [fname.split(' ')[1][fname.split(' ')[1].find('.') + 1:] for fname in lines if
                fname.find(' ... error generating.') > 0]


class SubprocessBasedWorker(Worker):
    def decompile(self):
        return subprocess.check_output(self.full_command())#, stderr=subprocess.STDOUT)

    def nice(self, value):
        return ['nice', '-n', str(value)]

    def timeout(self, seconds):
        return ['timeout', '-k', '30', str(seconds)]

    def full_command(self):
        command = self.decompiler_command
        if self.add_timeout:
            command = self.timeout(self.timeout_value) + command
        if self.add_nice:
            command = self.nice(self.nice_value) + command
        logging.debug('Command built: %s' % command)
        return command

    def process_clean():
        # Sometimes wine processes or xvfb continue running after the subprocess call ends.
        # So we need to kill them to avoid memory leaks
        for regex in [r'.+\.exe.*', r'.*wine.*', r'.*[xX]vfb.*']:
            subprocess.call(['pkill', regex])


class LibraryBasedWorker(Worker):
    def decompile(self):
        """ Should be overriden by subclasses.
        This should return output messages (if there are some), or '' if there isn't anything to return. """


# TODO: add support for subclasses that use libraries instead of externals programs with subprocess!
class CSharpWorker(SubprocessBasedWorker):
    def set_attributes(self):
        self.name = "csharp"
        self.decompiler_command = ["wine",
                                   "/just_decompile/ConsoleRunner.exe",
                                   "/target:" + self.get_tmpfs_file_path(),
                                   "/out:" + self.get_tmpfs_folder_path()]


# This function should by called by redis queue (rq command).
def pe_worker_for_redis(task):
    worker = CSharpWorker(task['sample'])
    send_result(worker.process())
    return


def send_result(result):
    url = "http://api:8000/set_result"
    payload = {'result': str(result)}
    response = requests.post(url, payload)
    while response.status_code != 200:
        time.sleep(10)
        logging.info('Status code is %s. Retrying...' % response.status_code)
        try:
            response = requests.post(url, payload)
        except (requests.ConnectionError, requests.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            logging.info("Connection error or timeout. Retrying...")
            pass  # Retry
    return response
