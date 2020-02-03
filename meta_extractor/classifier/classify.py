import logging

from .classifiers import CLASSIFIERS


def get_identifier_of_file(sample: bytes) -> str:
    sample_identifier = None
    for identifier, classifier_function in CLASSIFIERS.items():
        if classifier_function(sample):
            sample_identifier = identifier
            break
    logging.info(f'File type detected: {sample_identifier}')
    return sample_identifier
