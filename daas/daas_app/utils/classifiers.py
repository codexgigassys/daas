from .mime_type import mime_type, pe_mime_types, flash_mime_types, apk_mime_types


def pe_classifier(data):
    return mime_type(data) in pe_mime_types


def flash_classifier(data):
    return mime_type(data) in flash_mime_types


def apk_classifier(data):
    return mime_type(data) in apk_mime_types
