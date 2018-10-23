import magic


pe_mime_types = ["application/vnd.microsoft.portable-executable",
                 "application/x-dosexec",
                 "application/x-msi",
                 "application/x-ms-dos-executable"]


flash_mime_types = ["application/x-shockwave-flash",
                    "application/vnd.adobe.flash.movie"]


def mime_type(data):
    return magic.from_buffer(data, mime=True)
