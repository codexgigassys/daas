from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
import ast
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .forms import UploadFileForm
from .config import ALLOW_SAMPLE_DOWNLOAD
from .models import Sample, Result, RedisJob
from .utils.upload_file import upload_file
from .utils import classifier
from .utils import result_status
from .utils.charts.chart_cache import ChartCache
from .utils.reprocess import reprocess
from .view_utils import download


class IndexRedirectView(LoginRequiredMixin, generic.View):
    def get(self, request):
        return HttpResponseRedirect(reverse_lazy('index'))


class IndexView(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class UpdateStatisticsView(LoginRequiredMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'daas_app.update_statistics_permission'

    def get(self, request):
        ChartCache().update_charts()
        return HttpResponseRedirect(self.request.path_info)


class StatisticsView(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/statistics.html'
    chart_name = None

    def get(self, request):
        time_since_last_update = ChartCache().time_since_last_update_as_string
        return render(request, 'daas_app/statistics.html', {'charts': ChartCache().charts_of_group(self.chart_name),
                                                            'time_since_last_update': time_since_last_update})


class SamplesPerElapsedTimeView(StatisticsView):
    chart_name = 'Samples per elapsed time'


class SamplesPerSizeView(StatisticsView):
    chart_name = 'Samples per size'


class SamplesPerTypeView(StatisticsView):
    chart_name = 'Samples per type'


class SamplesPerUploadDateView(StatisticsView):
    chart_name = 'Samples per upload date'


class SamplesPerProcessDateView(StatisticsView):
    chart_name = 'Samples per process date'


class SamplesPerDecompilationStatusView(StatisticsView):
    chart_name = 'Samples per decompilation status'


class SampleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'daas_app.delete_sample_permission'

    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'
    permission_required = 'daas_app.delete_sample_permission'


@login_required
@permission_required('upload_sample_permission')
def reprocess_view(request, sample_id):
    reprocess(Sample.objects.get(id=sample_id))
    return HttpResponseRedirect(reverse('index'))


@login_required
@permission_required('upload_sample_permission')
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content = request.FILES['file'].file.read()
            name = request.FILES['file'].name
            try:
                already_exists, _ = upload_file(name, content)
            except classifier.ClassifierError:
                return HttpResponseRedirect(reverse('no_filter_found'))
            else:
                return HttpResponseRedirect(reverse('index')) if not already_exists else HttpResponseRedirect(reverse('file_already_uploaded'))
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
    sample = Sample.objects.get(id=sample_id)
    # With the following 'if' nobody will be allowed to download samples if the config say so,
    # even if they manually craft a download url.
    file_content = sample.data if ALLOW_SAMPLE_DOWNLOAD else b''
    return download(file_content, sample.name, "application/octet-stream")


@login_required
@permission_required('download_source_code_permission')
def download_source_code_view(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    zipped_source_code = sample.result.source_code
    return download(zipped_source_code, sample.name, "application/x-zip-compressed", extension='.zip')


@login_required
@permission_required('cancel_job_permission')
def cancel_job_view(request, redis_job_pk):
    RedisJob.objects.get(pk=redis_job_pk).cancel()
    return HttpResponseRedirect(reverse_lazy('index'))


class SetResult(APIView):
    def post(self, request):
        result = ast.literal_eval(request.POST['result'])
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        status = result_status.TIMED_OUT if result['statistics']['timed_out'] else\
            (result_status.SUCCESS if result['statistics']['decompiled'] else result_status.FAILED)
        output = result['statistics']['output']
        zip = result['zip']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            Result.objects.filter(sample=sample).delete()
            result = Result.objects.create(timeout=timeout, elapsed_time=elapsed_time,
                                           exit_status=exit_status, status=status, output=output,
                                           zip_result=zip, decompiler=decompiler, version=version,
                                           sample=sample)
            result.save()
        return Response({'message': 'ok'})
