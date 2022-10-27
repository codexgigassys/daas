import logging

from .classifiers import CLASSIFIERS


def get_identifier_of_file(sample_content: bytes) -> str:
    sample_identifier = None
    for classifier in CLASSIFIERS:
        if classifier.match(sample_content):
            sample_identifier = classifier.file_type
            break
    logging.info(f'File type detected: {sample_identifier}')
    return sample_identifier
