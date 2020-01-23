from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views import generic
import hashlib
import logging
from typing import BinaryIO

from .utils.mixins import UploadMixin
from ..forms import UploadFileForm
from ..models import Sample


class UploadView(UploadMixin, generic.View):
    def post(self, request: HttpRequest) -> HttpResponse:
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']

            # We already have the file on the view, so we will check whether it already exists or not at this endpoint.
            try:
                Sample.objects.get(sha1=self._get_file_sha1(file))
            except Sample.DoesNotExist:
                successfully_uploaded = self.upload(file=file,
                                                    zip_password=form.cleaned_data.get('zip_password', ''))
                response = HttpResponseRedirect(reverse('index')) if successfully_uploaded else HttpResponseBadRequest()
            else:
                response = HttpResponseRedirect(reverse('file_already_uploaded'))
        else:
            logging.warning('Invalid form for upload_file_view.')
            response = HttpResponseBadRequest()
        return response

    def get(self, request: HttpRequest) -> HttpResponse:
        form = UploadFileForm()
        return render(request, 'daas_app/upload.html', {'form': form})

    def _get_file_sha1(self, file: BinaryIO) -> str:
        sha1 = hashlib.sha1(file.read()).hexdigest()
        file.seek(0)
        return sha1


@login_required
def file_already_uploaded_view(request):
    return render(request, 'daas_app/file_already_uploaded.html')
