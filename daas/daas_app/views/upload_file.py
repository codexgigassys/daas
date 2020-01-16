from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import logging

from ..forms import UploadFileForm


@login_required
@permission_required('upload_sample_permission')
def upload_file_view(request):
    if request.method == 'POST':
        raise Exception('REWORK THIS METHOD TO SHARE LOGIC WITH API/UPLOAD.PY')  # fixme
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            zip_password = bytes(form.cleaned_data.get('zip_password', '').encode('utf-8'))
            file = 1 #create_and_upload_file(file_name=form.cleaned_data['file'].name,
                     #                     content=form.cleaned_data['file'].read(),
                     #                     force_reprocess=False,
                     #                     zip_password=zip_password)
            if not file:
                logging.info('Upload file: No filter found for the given file.')
                return HttpResponseRedirect(reverse('no_filter_found'))
            else:
                logging.info('Upload file: filter found for the given file.')
                return HttpResponseRedirect(reverse('index')) if not file.already_exists else HttpResponseRedirect(reverse('file_already_uploaded'))
        else:
            logging.warning('Invalid form for upload_file_view.')
            return HttpResponseBadRequest()
    else:  # GET
        form = UploadFileForm()
        return render(request, 'daas_app/upload.html', {'form': form})


@login_required
def file_already_uploaded_view(request):
    return render(request, 'daas_app/file_already_uploaded.html')


@login_required
def no_filter_found_view(request):
    return render(request, 'daas_app/no_filter_found.html')
