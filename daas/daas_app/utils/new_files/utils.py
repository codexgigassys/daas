import logging
from typing import Optional

from .. import classifier
from .abstract_new_file import AbstractNewFile
from .new_sample_pack_file import NewSamplePackFile
from .new_sample_file import NewSampleFile


def create_file_instance(file_name: str, content: bytes, force_reprocess: bool = False,
                         zip_password: bytes = b'') -> Optional[AbstractNewFile]:
    try:
        identifier = classifier.get_identifier_of_file(content)
    except classifier.ClassifierError:
        logging.info(f'There is no valid processor for file: {file_name}.')
        return None
    else:
        sample_file_class = NewSamplePackFile if identifier == 'zip' else NewSampleFile
        return sample_file_class(file_name, content, identifier, force_reprocess, zip_password)


def create_and_upload_file(file_name: str, content: bytes, force_reprocess: bool = False,
                           zip_password: bytes = b'') -> Optional[AbstractNewFile]:
    file = create_file_instance(file_name, content, force_reprocess, zip_password)
    if file:
        file.upload()
    return file
