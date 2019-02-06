import magic


pe_mime_types = ["application/vnd.microsoft.portable-executable",
                 "application/x-dosexec",
                 "application/x-msi",
                 "application/x-ms-dos-executable"]


flash_mime_types = ["application/x-shockwave-flash",
                    "application/vnd.adobe.flash.movie"]


apk_mime_types = ["application/vnd.android.package-archive"]


zip_mime_types = ["application/zip",
                  "application/x-zip-compressed",
                  "multipart/x-zip"]


def mime_type(data):
    return magic.from_buffer(data, mime=True)


def description(data):
    try:
        file_description = magic.from_buffer(data, mime=False)
    except magic.MagicException:
        file_description = "undefined"
    return file_description if file_description != "" else "undefined"


def has_csharp_description(data):
    return description(data).find('Mono') >= 0
