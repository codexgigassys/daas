import os
import shutil
import logging
import subprocess
from functools import reduce

from .utils import to_bytes
from .exceptions import CantDecompileJavaException


def subprocess_command_to_string(command):
    return reduce(lambda part1, part2: part1 + ' ' + part2, command)


def binary_path_to_directory(path):
    """ abc/cde/0000/file.php -> abc/cde/000 """
    return reduce(lambda x, y: x + '/' + y, path.split('/')[0:path.count('/')])


def apk_to_jar_failed(jar_base_path, jar_path):
    error_file_detected = (not os.path.isfile(jar_path)) and any(path.find('error') >= 0 for path in os.listdir(jar_base_path))
    if error_file_detected:
        logging.error('[apk -> jar] FAILED')
        logging.error(f'[apk -> jar] os.listdir(%s): %s' % (jar_base_path, os.listdir(jar_base_path)))
    return error_file_detected


def run_apk_to_jar_command(jar_base_path, jar_path, command) -> bytes:
    try:
        output = subprocess.check_output(command, cwd=jar_base_path)
    except subprocess.CalledProcessError as e:
        if apk_to_jar_failed(jar_base_path, jar_path):
            raise e
        else:
            output = e.output
    if output.lower().find(b'java.nio.Buffer.position'.lower()) and apk_to_jar_failed(jar_base_path, jar_path):
        logging.error('[apk -> jar] Raising CantDecompileJavaException() [java.nio.Buffer.position error]')
        logging.error(output)
        raise CantDecompileJavaException()
    return to_bytes(output)


def apk_to_jar(apk_path) -> bytes:
    # Receives the full apk, extracts the *.dex file and transforms it into a *.jar file
    logging.debug('[apk -> jar] APK Path: %s' % apk_path)
    jar_base_path = binary_path_to_directory(apk_path)
    jar_path = jar_base_path + '/' + 'jar.jar'
    command = ['nice', '-n', '2', 'timeout', '-k', '30', '360', 'sh', '/dex2jar/d2j-dex2jar.sh', '--force',
               apk_path, '-o', jar_path]
    logging.debug('[apk -> jar] Command: %s' % subprocess_command_to_string(command))
    output = run_apk_to_jar_command(jar_base_path, jar_path, command)
    if apk_to_jar_failed(jar_base_path, jar_path):
        logging.error('[apk -> jar] dex2jar failed!')
        logging.error('[apk -> jar] printing dex2jar output: %s' % output)
        logging.debug('[apk -> jar] Present files at jar_base_path: %s' % os.listdir(jar_base_path))
        error_files = filter(lambda path: path.find('error') >= 0, os.listdir(jar_base_path))
        for error_file in error_files:
            remove(jar_base_path + '/' + error_file)
        logging.debug('[apk -> jar] Error files removed.')
    logging.debug('[apk -> jar] Jar path: %s' % jar_path)
    logging.debug('[apk -> jar] os.listdir(%s): %s' % (jar_base_path, os.listdir(jar_base_path)))
    logging.debug('[apk -> jar] OK. Transformed: apk -> jar')
    return jar_path, to_bytes(output)


def jar_to_java(jar_path, output_directory) -> bytes:
    logging.debug('[jar -> java] Jar Path: %s' % jar_path)
    if not os.path.isfile(jar_path):
        logging.error('[jar -> java] Jar path %s is not the path of a file.' % jar_path)
        jar_base_path = binary_path_to_directory(jar_path)
        logging.error('[jar -> java] os.listdir(%s): %s' % (jar_base_path, os.listdir(jar_base_path)))
        raise Exception('[jar -> java] Invalid jar file for jd-cli')
    command = ['nice', '-n', '2', 'timeout', '-k', '30', '360', 'java', '-jar', '/jd-cli/jd-cli.jar',
               jar_path, '-od', output_directory]
    logging.debug('[jar -> java] Command: %s' % subprocess_command_to_string(command))
    output = subprocess.check_output(command)
    logging.debug('[jar -> java] Transformed: jar -> java')
    logging.debug('[jar -> java] Java path: %s' % output_directory)
    return to_bytes(output)


def merge_folders(source_directory, destination_directory):
    """ Merges folder recursively. If a file is present only at one directory (source or destination), it is preserved.
        If a file is present at both directories, we replace the file at destination directory with the file from
        source directory.
        Source: https://lukelogbook.tech/2018/01/25/merging-two-folders-in-python/ """
    for src_dir, dirs, files in os.walk(source_directory):
        dst_dir = src_dir.replace(source_directory, destination_directory, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)
