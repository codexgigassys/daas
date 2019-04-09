from .file_utils import mime_type, has_csharp_description, pe_mime_types, flash_mime_types, apk_mime_types, java_mime_types


def pe_classifier(data):
    return mime_type(data) in pe_mime_types and has_csharp_description(data)


def flash_classifier(data):
    return mime_type(data) in flash_mime_types


def apk_classifier(data):
    return mime_type(data) in apk_mime_types


def java_classifier(data):
    return mime_type(data) in java_mime_types
