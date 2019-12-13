import logging

from .classifier.file_utils import get_in_memory_zip_of


def save_and_get_metadata_of_zip_subfiles(sample: bytes, zip_password: bytes, force_reprocess: bool) -> None:
    logging.info('Processing zip file.')
    zip_file = get_in_memory_zip_of(sample)
    for file_name in zip_file.namelist():
        content = zip_file.read(file_name, pwd=zip_password)
        # todo: upload file and get it's meta, then return a list with the metadata of all files.
        # before processing a file, determine whether it should be processed or not
