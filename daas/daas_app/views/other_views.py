from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import logging

from ..forms import UploadFileForm
from ..config import ALLOW_SAMPLE_DOWNLOAD
from ..models import Sample, RedisJob
from ..utils.new_files import create_and_upload_file
from ..utils.reprocess import reprocess
from ..view_utils import download
from ..filters import SampleFilter


class IndexRedirectView(LoginRequiredMixin, generic.View):
    def get(self, request):
        return HttpResponseRedirect(reverse_lazy('index'))


class IndexView(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/index.html'
    filterset_class = SampleFilter

    def get(self, request):
        sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all())
        return render(request, 'daas_app/index.html', {'sample_filter': sample_filter})


class SampleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.DeleteView):
    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'
    permission_required = 'daas_app.delete_sample_permission'


@login_required
@permission_required('upload_sample_permission')
def reprocess_view(request, sample_id):
    logging.info('Reprocessing sample: %s' % sample_id)
    reprocess(Sample.objects.get(id=sample_id), force_reprocess=True)
    return HttpResponseRedirect(reverse('index'))


@login_required
@permission_required('upload_sample_permission')
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            zip_password = bytes(form.cleaned_data.get('zip_password', '').encode('utf-8'))
            file = create_and_upload_file(file_name=form.cleaned_data['file'].name,
                                          content=form.cleaned_data['file'].read(),
                                          force_reprocess=False,
                                          zip_password=zip_password)
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


@login_required
@permission_required('download_sample_permission')
def download_sample_view(request, sample_id):
    logging.info('downloading sample: id=%s' % sample_id)
    sample = Sample.objects.get(id=sample_id)
    # With the following 'if' nobody will be allowed to download samples if the config say so,
    # even if they manually craft a download url.
    file_content = sample.data if ALLOW_SAMPLE_DOWNLOAD else b''
    return download(file_content, sample.name, "application/octet-stream")


@login_required
@permission_required('download_source_code_permission')
def download_source_code_view(request, sample_id):
    logging.info('downloading source code: sample_id=%s' % sample_id)
    sample = Sample.objects.get(id=sample_id)
    zipped_source_code = sample.result.compressed_source_code.tobytes()
    return download(zipped_source_code, sample.name, "application/x-zip-compressed", extension=sample.result.extension)


@login_required
@permission_required('cancel_job_permission')
def cancel_job_view(request, redis_job_pk):
    RedisJob.objects.get(pk=redis_job_pk).cancel()
    return HttpResponseRedirect(reverse_lazy('index'))
