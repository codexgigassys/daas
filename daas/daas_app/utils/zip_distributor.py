import logging

from . import upload_file
from .file_utils import get_in_memory_zip_of
from . import classifier


def upload_files_of(zip_binary: str, zip_password: bytes = None):
    zip_file = get_in_memory_zip_of(zip_binary)
    any_already_exist = False
    any_should_reprocess = False
    for file_name in zip_file.namelist():
        content = zip_file.read(file_name, pwd=zip_password)
        try:
            already_exists, should_process = upload_file.upload_file(file_name, content)
        except classifier.ClassifierError:
            logging.debug(f'There is no valid processor for file: {file_name}')
        else:
            any_already_exist = any_already_exist or already_exists
            any_should_reprocess = any_should_reprocess or should_process
    return any_already_exist, any_should_reprocess
