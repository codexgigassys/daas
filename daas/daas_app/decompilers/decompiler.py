import subprocess
import logging
import time
import os
from .utils import remove_file, remove_directory, has_a_non_empty_file
import hashlib
import shutil
import re


class AbstractDecompiler:
    def __init__(self, decompiler_name, file_type):
        self.file_type = file_type
        self.decompiler_name = decompiler_name
        self.safe_file_type = re.sub('\W+', '', file_type)
        logging.debug("Decompiler initialized: %s" % file_type)

    def set_sample(self, sample):
        self.clean()
        self.save_sample(sample)
        self.create_tmpfs_folder()

    def save_sample(self, sample):
        self.sample = sample
        self.sha1 = hashlib.sha1(sample).hexdigest()
        file_ = open(self.get_tmpfs_file_path(), 'wb')
        file_.write(sample)
        file_.close()
        logging.debug("Sample saved to: %s" % self.get_tmpfs_file_path())

    def create_tmpfs_folder(self):
        os.mkdir(self.get_tmpfs_folder_path())
        logging.debug("Extraction folder created: %s" % self.get_tmpfs_folder_path())

    def get_tmpfs_folder_path(self):
        # All workers use the same path for the same file type because they run on different containers,
        # so race conditions between them are impossible
        return '/tmpfs/%s' % self.safe_file_type

    def get_tmpfs_file_path(self):
        return '/tmpfs/%s.sample' % self.safe_file_type

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

    def process(self, sample):
        self.set_sample(sample)
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
            logging.debug('Subprocess raised CalledProcessError exception. Duration: %s seconds. Timeout: %s seconds' % (elapsed_time, self.timeout))
            decompiled = False
            # Exception handling
            if exit_status == 124:  # exit status is 124 when the timeout is reached.
                logging.debug('Process timed out.')
            else:
                logging.debug('Unknown exit status code: %s.' % exit_status)
        info_for_statistics = {'sha1': self.sha1,
                               'timeout': self.timeout,
                               'elapsed_time': elapsed_time + 1,
                               'exit_status': exit_status,
                               'timed_out': exit_status == 124,
                               'output': self.decode_output(output),
                               'errors': self.get_errors(output),
                               'decompiled': decompiled,
                               'decompiler': self.decompiler_name,
                               'type': self.file_type}
        return {'statistics': info_for_statistics, 'zip': zip}

    def get_errors(self, output):
        return []


class AbstractSubprocessBasedDecompiler(AbstractDecompiler):
    def __init__(self, decompiler_name, file_type, nice, timeout,
                 decompiler_command, processes_to_kill,
                 custom_current_working_directory):
        self.nice = nice
        self.timeout = timeout  # seconds
        self.decompiler_command = decompiler_command
        self.processes_to_kill = processes_to_kill
        self.custom_current_working_directory = custom_current_working_directory
        super().__init__(decompiler_name, file_type)

    def decompile(self):
        result = subprocess.check_output(self.full_command(),
                                         cwd=self.get_current_working_directory(),
                                         stderr=subprocess.STDOUT)
        self.process_clean()
        return result

    def add_nice(self):
        return self.nice != 0

    def add_timeout(self):
        return self.timeout > 0

    def get_current_working_directory(self):
        return self.custom_current_working_directory if self.custom_current_working_directory is not None else self.get_tmpfs_folder_path()

    def nice_command_part(self):
        return ['nice', '-n', str(self.nice)]

    def timeout_command_part(self):
        return ['timeout', '-k', '30', str(self.timeout)]

    def replace_paths(self, part):
        paths = {'@sample_path': self.get_tmpfs_file_path(),
                 '@extraction_path': self.get_tmpfs_folder_path()}
        for key, value in paths.items():
            part = part.replace(key, value)
        return part

    def full_command(self):
        command = [self.replace_paths(part) for part in self.decompiler_command]
        if self.add_timeout():
            command = self.timeout_command_part() + command
        if self.add_nice():
            command = self.nice_command_part() + command
        logging.debug('Command built: %s' % command)
        return command

    def process_clean(self):
        # Sometimes wine processes or xvfb continue running after the subprocess call ends.
        # So we need to kill them to avoid memory leaks
        for regex in [r'.*[xX]vfb.*', r'.*wine.*'] + self.processes_to_kill:
            subprocess.call(['pkill', regex])


class AbstractLibraryBasedDecompiler(AbstractDecompiler):
    def decompile(self):
        """ Should be overriden by subclasses.
        This should return output messages (if there are some), or '' if there isn't anything to return. """


class CSharpDecompiler(AbstractSubprocessBasedDecompiler):
    def get_errors(self, output):
        lines = str(output).replace('\r', '').split('\n')
        return [fname.split(' ')[1][fname.split(' ')[1].find('.') + 1:] for fname in lines if
                fname.find(' ... error generating.') > 0]


class FlashDecompiler(AbstractSubprocessBasedDecompiler):
    def set_attributes(self):
        self.file_type = "Flash"
        self.timeout = 12*60  # Sometimes ffdec takes a lot of time!
        self.decompiler_name = "FFDec"
        self.decompiler_command = ['ffdec', '-onerror', 'ignore', '-timeout', '600', '-exportTimeout',
                                   '600', '-exportFileTimeout', '600', '-export', 'all',
                                   self.get_tmpfs_folder_path(), self.get_tmpfs_file_path()]


