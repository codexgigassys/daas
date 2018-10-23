from .filter_utils import mime_type, pe_mime_types, flash_mime_types


def pe_filter(data):
    return mime_type(data) in pe_mime_types


def flash_filter(data):
    return mime_type(data) in flash_mime_types
