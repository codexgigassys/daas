from django.http import HttpResponse


def download(file_content: bytes, filename: str, content_type: str, extension: str = 'daas') -> HttpResponse:
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}.{extension}'  # force browser to download file
    response.write(file_content)
    return response
