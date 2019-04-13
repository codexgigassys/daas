from .file_utils import mime_type, has_csharp_description, pe_mime_types, flash_mime_types, apk_mime_types,\
    java_mime_types, zip_and_jar_shared_mime_types, has_java_structure, maybe_zip_mime_types, has_zip_structure


def pe_classifier(data):
    return mime_type(data) in pe_mime_types and has_csharp_description(data)


def flash_classifier(data):
    return mime_type(data) in flash_mime_types


def apk_classifier(data):
    return mime_type(data) in apk_mime_types


def java_classifier(data):
    return mime_type(data) in java_mime_types or (mime_type(data) in zip_and_jar_shared_mime_types
                                                  and has_java_structure(data))


def zip_classifier(data):
    return ((mime_type(data) in maybe_zip_mime_types and has_zip_structure(data))
            or (mime_type(data) in zip_and_jar_shared_mime_types and not java_classifier(data)))
