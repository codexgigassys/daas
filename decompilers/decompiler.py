import subprocess
import logging
import time
import os
import hashlib
import shutil
import re

from .utils import has_a_non_empty_file, shutil_compression_algorithm_to_extnesion, clean_directory


class AbstractDecompiler:
    def __init__(self, decompiler_name, file_type, extension, source_compression_algorithm, version):
        clean_directory('/tmpfs/')
        self.file_type = file_type
        self.extension = extension
        self.source_compression_algorithm = source_compression_algorithm
        self.decompiler_name = decompiler_name
        self.safe_file_type = re.sub(r'\W+', '', file_type)
        self.version = version
        logging.debug(f'Decompiler initialized: {file_type}')

    @property
    def source_code_extension(self):
        return shutil_compression_algorithm_to_extnesion(self.source_compression_algorithm)

    def set_sample(self, sample):
        self.save_sample(sample)
        self.create_tmpfs_folder()

    def save_sample(self, sample):
        self.sample = sample
        self.sha1 = hashlib.sha1(sample).hexdigest()
        with open(self.get_tmpfs_file_path(), 'wb') as file:
            file.write(sample)
        logging.debug(f'Sample saved to: {self.get_tmpfs_file_path()}')

    def create_tmpfs_folder(self):
        os.mkdir(self.get_tmpfs_folder_path())
        logging.debug(f'Extraction folder created: {self.get_tmpfs_folder_path()}')

    def get_tmpfs_folder_path(self):
        # All workers use the same path for the same file type because they run on different containers,
        # so race conditions among them are impossible
        return f'/tmpfs/{self.safe_file_type}'

    def get_tmpfs_file_path(self):
        return f'/tmpfs/{self.safe_file_type}.{self.extension}'

    @staticmethod
    def decode_output(output):
        try:
            return output.decode('utf-8').strip()
        except UnicodeDecodeError:
            return output.decode('utf-8', errors='replace').strip()

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
            self.clean_decompiled_content()
            # Zip file with decompiled source code
            shutil.make_archive('/tmpfs/code', self.source_compression_algorithm, self.get_tmpfs_folder_path())
            with open(f'/tmpfs/code.{self.source_code_extension}', 'rb') as file:
                zip = file.read()
            decompiled = self.something_decompiled()
        except subprocess.CalledProcessError as e:
            # Details and info for statistics
            zip = None
            elapsed_time = int(time.time() - start)
            exit_status = e.returncode
            output = e.output
            logging.debug(f'Subprocess raised CalledProcessError exception. Duration: {elapsed_time} seconds. Timeout: {self.timeout} seconds')
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
                               'decompiled': decompiled,
                               'decompiler': self.decompiler_name,
                               'version': self.version}
        return {'statistics': info_for_statistics,
                'source_code': {'file': zip,
                                'extension': self.source_code_extension}}

    def decompile(self):
        """ Should be overridden by subclasses.
        This should return output messages (if there are some), or None if there isn't anything to return. """
        raise NotImplementedError()

    def clean_decompiled_content(self):
        """ Here you can access the decompiled files and clean them if you want to remove or modify useless data. """
        pass


class SubprocessBasedDecompiler(AbstractDecompiler):
    def __init__(self, decompiler_name, file_type, extension, source_compression_algorithm, nice, timeout,
                 creates_windows, decompiler_command, processes_to_kill,
                 custom_current_working_directory, version):
        self.nice = nice
        self.timeout = timeout  # seconds
        self.creates_windows = creates_windows
        self.decompiler_command = decompiler_command
        self.processes_to_kill = processes_to_kill
        self.custom_current_working_directory = custom_current_working_directory
        super().__init__(decompiler_name, file_type, extension, source_compression_algorithm, version)

    def decompile(self):
        result = subprocess.check_output(self.full_command(),
                                         cwd=self.get_current_working_directory(),
                                         stderr=subprocess.STDOUT)
        self.process_clean()
        return result

    def requires_nice(self):
        return self.nice != 0

    def requires_timeout(self):
        return self.timeout > 0

    def get_current_working_directory(self):
        return self.custom_current_working_directory if self.custom_current_working_directory else self.get_tmpfs_folder_path()

    def nice_command_arguments(self):
        return ['nice', '-n', str(self.nice)]

    def timeout_command_arguments(self):
        return ['timeout', '-k', '30', str(self.timeout)]

    def xvfb_command_arguments(self):
        return ['xvfb-run']

    def replace_paths(self, argument):
        paths = {'@sample_path': self.get_tmpfs_file_path(),
                 '@extraction_path': self.get_tmpfs_folder_path()}
        for key, value in paths.items():
            argument = argument.replace(key, value)
        return argument

    def start_new_argument(self, split_command, argument):
        argument = argument.strip()
        if argument is not '':
            split_command.append(argument)
        return ''

    def split_command(self):
        split_command = []
        concatenate = False
        argument = ''
        for character in self.decompiler_command:
            if character == " ":
                if concatenate:
                    argument += character
                else:
                    argument = self.start_new_argument(split_command, argument)
            elif character == "\'":
                concatenate = not concatenate
                # if quotes are being closed, then an argument just finished
                if not concatenate:
                    argument = self.start_new_argument(split_command, argument)
            else:
                argument += character
        self.start_new_argument(split_command, argument)
        logging.debug(f'split_command: {self.decompiler_command} -> {split_command}')
        return split_command

    def full_command(self):
        command = [self.replace_paths(argument) for argument in self.split_command()]

        if self.requires_timeout():
            command = self.timeout_command_arguments() + command

        if self.requires_nice():
            command = self.nice_command_arguments() + command

        if self.creates_windows:
            command = self.xvfb_command_arguments() + command

        logging.debug('Command built: %s' % command)
        return command

    def process_clean(self):
        # Sometimes wine processes or xvfb continue running after the subprocess call ends.
        # So we need to kill them to avoid memory leaks
        for regex in [r'.*[xX]vfb.*', r'.*wine.*'] + self.processes_to_kill:
            subprocess.call(['pkill', regex])
