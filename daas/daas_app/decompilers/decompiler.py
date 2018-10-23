import subprocess
import logging
import time
import os
from .utils import remove_file, remove_directory, has_a_non_empty_file
import requests
import hashlib
import shutil


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
        self.processes_to_kill = []
        self.decompiler_name = "Name of the program used to decompile on this worker!"
        # Override this only if needed
        self.current_working_directory = self.get_tmpfs_folder_path()
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
        remove_file('/tmpfs/code.zip')
        remove_directory(self.get_tmpfs_folder_path())

    def decode_output(self, output):
        try:
            return output.decode("utf-8").strip()
        except UnicodeDecodeError:
            return output.decode("utf-8", errors="replace").strip()

    def something_decompiled(self):
        return has_a_non_empty_file(self.get_tmpfs_folder_path())

    def process(self):
        start = time.time()
        try:
            start = time.time()
            output = self.decompile()
            # Details and info for statistics
            elapsed_time = int(time.time() - start)
            exit_status = 0  # The decompiler didn't crash
            # Zip file with decompiled source code
            shutil.make_archive('/tmpfs/code', 'zip', self.get_tmpfs_folder_path())
            file = open('/tmpfs/code.zip', 'rb')
            zip = file.read()
            file.close()
            decompiled = self.something_decompiled()
        except subprocess.CalledProcessError as e:
            # Details and info for statistics
            zip = None
            elapsed_time = int(time.time() - start)
            exit_status = e.returncode
            output = e.output
            logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (elapsed_time, self.timeout_value))
            decompiled = False
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
                               'errors': self.get_errors(output),
                               'decompiled': decompiled,
                               'decompiler': self.decompiler_name,
                               'type': self.name}
        return {'statistics': info_for_statistics, 'zip': zip}

    def get_errors(self, output):
        return None


class SubprocessBasedWorker(Worker):
    def decompile(self):
        result = subprocess.check_output(self.full_command(),
                                         cwd=self.current_working_directory,
                                         stderr=subprocess.STDOUT)
        self.process_clean()
        return result

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

    def process_clean(self):
        # Sometimes wine processes or xvfb continue running after the subprocess call ends.
        # So we need to kill them to avoid memory leaks
        for regex in [r'.*[xX]vfb.*', r'.*wine.*'] + self.processes_to_kill:
            subprocess.call(['pkill', regex])


class LibraryBasedWorker(Worker):
    def decompile(self):
        """ Should be overriden by subclasses.
        This should return output messages (if there are some), or '' if there isn't anything to return. """


class CSharpWorker(SubprocessBasedWorker):
    def set_attributes(self):
        self.name = "C#"
        self.decompiler_name = "Just Decompile"
        self.processes_to_kill = [r'.+\.exe.*']
        self.decompiler_command = ["wine",
                                   "/just_decompile/ConsoleRunner.exe",
                                   "/target:" + self.get_tmpfs_file_path(),
                                   "/out:" + self.get_tmpfs_folder_path()]

    def get_errors(self, output):
        lines = str(output).replace('\r', '').split('\n')
        return [fname.split(' ')[1][fname.split(' ')[1].find('.') + 1:] for fname in lines if
                fname.find(' ... error generating.') > 0]


class FlashWorker(SubprocessBasedWorker):
    def set_attributes(self):
        self.name = "Flash"
        self.timeout_value = 12*60  # Sometimes ffdec takes a lot of time!
        self.decompiler_name = "FFDec"
        self.decompiler_command = ['ffdec', '-onerror', 'ignore', '-timeout', '600', '-exportTimeout',
                                   '600', '-exportFileTimeout', '600', '-export', 'all',
                                   self.get_tmpfs_folder_path(), self.get_tmpfs_file_path()]


# This function should by called by redis queue (rq command).
def redis_worker(task, decompiler):
    worker = decompiler(task['sample'])
    send_result(worker.process())


def pe_redis_worker(task):
    redis_worker(task, CSharpWorker)
    return


def flash_redis_worker(task):
    redis_worker(task, FlashWorker)
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
