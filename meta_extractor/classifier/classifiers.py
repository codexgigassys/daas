from .file_utils import (mime_type, has_csharp_description, pe_mime_types, flash_mime_types, java_mime_types,
                         has_java_structure, zip_mime_types, has_zip_structure)


class CSharpClassifier:
    file_type = 'pe'

    def match(self, data: bytes) -> bool:
        return mime_type(data) in pe_mime_types and has_csharp_description(data)


class FlashClassifier:
    file_type = 'flash'

    def match(self, data: bytes) -> bool:
        return mime_type(data) in flash_mime_types


class JavaClassifier:
    file_type = 'java'

    def match(self, data: bytes) -> bool:
        return mime_type(data) in java_mime_types or (mime_type(data) in zip_mime_types and has_java_structure(data))


class ZipClassifier:
    file_type = 'zip'

    def match(self, data: bytes) -> bool:
        return mime_type(data) in zip_mime_types and has_zip_structure(data) and not has_java_structure(data)


# Order is important! For instance, if you put zip classifier first, java files will be detected as zips.
CLASSIFIERS = [CSharpClassifier(), FlashClassifier(), JavaClassifier(), ZipClassifier()]
