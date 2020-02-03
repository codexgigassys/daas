import magic
from io import BytesIO
import zipfile
import logging


pe_mime_types = ['application/vnd.microsoft.portable-executable',
                 'application/x-dosexec',
                 'application/x-msi',
                 'application/x-ms-dos-executable']


flash_mime_types = ['application/x-shockwave-flash',
                    'application/vnd.adobe.flash.movie']


apk_mime_types = ['application/vnd.android.package-archive']


zip_and_jar_shared_mime_types = ['application/zip',
                                 'application/x-zip-compressed',
                                 'multipart/x-zip']

maybe_zip_mime_types = ['application/octet-stream']


java_mime_types = ['application/x-java-archive',
                   'application/java-archive']


def mime_type(data: bytes) -> str:
    return magic.from_buffer(data, mime=True)


def description(data: bytes) -> str:
    try:
        file_description = magic.from_buffer(data, mime=False)
    except magic.MagicException:
        file_description = 'undefined'
    return file_description if file_description != '' else 'undefined'


def has_csharp_description(data: bytes) -> bool:
    return description(data).find('Mono') >= 0


def get_in_memory_zip_of(zip_binary: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(BytesIO(zip_binary))


def has_zip_structure(data: bytes) -> bool:
    try:
        get_in_memory_zip_of(data)
    except zipfile.BadZipfile:
        return False
    except Exception as e:
        logging.exception('Error trying to create a ZipFile instance: %s' % e)
        return False
    else:
        return True


def has_java_structure(data: bytes) -> bool:
    """ Criteria based on public documentation of JAR format:
        https://docs.oracle.com/javase/7/docs/technotes/guides/jar/jar.html """
    if has_zip_structure(data):
        zip_object = get_in_memory_zip_of(data)
        zip_files = zip_object.namelist()
        return (any(file.strip() == 'META-INF/MANIFEST.MF' for file in zip_files)
                and any(file.find('.class') > 0 for file in zip_files))
