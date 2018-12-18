import zipfile
from io import BytesIO
import logging
import hashlib

from . import upload_file
from .mime_type import mime_type, zip_mime_types
from . import classifier


def get_in_memory_zip_of(zip_binary):
    """
    :param zip_binary: Bytes of a zip file.
    :return: An in memory file descriptor for the given binary.
    """
    zip_file = BytesIO()
    zip_file.write(zip_binary)
    new_zip = zipfile.ZipFile(zip_file)
    return new_zip


def upload_files_of(zip_binary):
    zip_file = get_in_memory_zip_of(zip_binary)
    any_already_exist = False
    any_should_reprocess = False
    for name in zip_file.namelist():
        content = zip_file.read(name)
        sha1 = hashlib.sha1(content).hexdigest()
        try:
            already_exists, should_process = upload_file.upload_file(name, content)
        except classifier.ClassifierError:
            logging.debug('There are no valid processor for file: %s [%s]' % (name, sha1))
        else:
            if already_exists:
                logging.debug('File already uploaded: %s [%s]' % (name, sha1))
            else:
                logging.debug('File uploaded correctly: %s [%s]' % (name, sha1))
            any_already_exist = any_already_exist or already_exists
            any_should_reprocess = any_should_reprocess or should_process
    return any_already_exist, any_should_reprocess


def is_zip(binary):
    return mime_type(binary) in zip_mime_types
