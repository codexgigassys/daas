import hashlib

from .classifier import get_identifier_of_file


def get_sample_metadata(sample: bytes) -> dict:
    return {'size': len(sample),
            'md5': hashlib.md5(sample).hexdigest(),
            'sha1': hashlib.sha1(sample).hexdigest(),
            'sha2': hashlib.sha256(sample).hexdigest(),
            'file_type': get_identifier_of_file(sample)}
