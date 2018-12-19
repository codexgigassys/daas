from django.http import HttpResponse


def download(file_content, filename, content_type, extension='.daas'):
    filename += extension
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename  # force browser to download file
    response.write(file_content)
    return response
