from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .utils.redis_manager import RedisManager, RedisManagerException
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Sample, Statistics, RedisJob
import ast
import hashlib
from django.urls import reverse_lazy
from django.db import IntegrityError
from .config import SAVE_SAMPLES, ALLOW_SAMPLE_DOWNLOAD
import logging
from django.db import transaction


class IndexView(generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class StatisticsView(generic.View):
    """ Decompiled samples per size """
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        keys = ['charttype', 'chartdata', 'chartcontainer', 'extra']
        charts = [samples_per_elapsed_time_chart(),
                  samples_per_size_chart(),
                  sample_per_decompiler_chart(),
                  sample_per_decompilation_result_chart()]
        data = {}
        index = 0
        for chart in charts:
            for key in keys:
                value = chart.pop(key)
                chart[key + str(index)] = value
            data.update(chart)
            index += 1
        return render(request, 'daas_app/statistics.html', data)


def samples_per_size_chart():
    size_list = [int(sample.size/1024) for sample in Sample.objects.exclude(statistics__isnull=True) if sample.statistics.exit_status == 0]
    ydata = [0, 0, 0, 0]
    for size in size_list:
        position = len(str(size)) - 2
        ydata[position] += 1
    xdata = ["0 - 100 Kb", "100 Kb - 1 Mb", "1 Mb - 10 Mb", "+ 10 Mb"]
    chartdata = {'x': xdata, 'y': ydata}
    data = {
        'charttype': "discreteBarChart",
        'chartdata': chartdata,
        # If two charts the same chartcontainer value, then only one of them will be displayed
        'chartcontainer': 'samples_per_size_chart_container',
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return data


def samples_per_elapsed_time_chart():
    times = [statistic.elapsed_time for statistic in Statistics.objects.filter(exit_status=0)]
    ydata = [0, 0, 0, 0, 0, 0, 0]
    for time in times:
        position = int(time/5) if time < 30 else 7
        ydata[position] += 1
    xdata = ["0 - 4", "5 - 9", "10 - 14", "15 - 19", "20 - 24", "25 - 29", "30 / +"]
    chartdata = {'x': xdata, 'y': ydata}
    data = {
        'charttype': "discreteBarChart",
        'chartdata': chartdata,
        'chartcontainer': 'samples_per_elapsed_time_chart_container',
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return data


def sample_per_decompiler_chart():
    xdata = Sample.objects.order_by('file_type').values_list('file_type', flat=True).distinct('file_type')
    ydata = [Sample.objects.filter(file_type=file_type).count() for file_type in xdata]
    chartdata = {'x': xdata, 'y': ydata}
    data = {
        'charttype': "pieChart",
        'chartdata': chartdata,
        'chartcontainer': 'samples_per_decompiler_chart_container',
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return data


def sample_per_decompilation_result_chart():
    xdata = ["Ok", "Time out", "Failed"]
    ydata = [Statistics.objects.filter(decompiled=True).count(),
             Statistics.objects.filter(timed_out=True).count(),
             Statistics.objects.filter(decompiled=False).filter(timed_out=False).count()]
    chartdata = {'x': xdata, 'y': ydata}
    data = {
        'charttype': "pieChart",
        'chartdata': chartdata,
        'chartcontainer': 'samples_per_decompilation_result_chart_container',
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return data


class SampleDeleteView(generic.edit.DeleteView):
    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'


def process_file(sample, content):
    """ this is not a view """
    file_type, job_id = RedisManager().submit_sample(content)
    RedisJob.objects.create(job_id=job_id, sample=sample)
    sample.file_type = file_type
    sample.save()


def reprocess(request, sample_id):
    # If we didn't save the sample, we have no way to decompile it again using this view
    sample = Sample.objects.get(id=sample_id)
    if sample.content_saved():
        logging.debug('Reprocessing sample: %s' % sample_id)
        process_file(sample, sample.data.tobytes())
    else:
        # It's not necessary to return a proper error here, because the URL will not be accessible via GUI
        # if the sample is not saved.
        logging.error('It was not possible to reprocess sample %s because it was not saved.' % sample_id)
    return HttpResponseRedirect(reverse('index'))


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content = request.FILES['file'].file.read()
            name = request.FILES['file'].name
            md5 = hashlib.md5(content).hexdigest()
            sha1 = hashlib.sha1(content).hexdigest()
            sha2 = hashlib.sha256(content).hexdigest()
            try:
                # We will add file_type and redis_job later
                sample = Sample.objects.create(data=(content if SAVE_SAMPLES else None), md5=md5,
                                               sha1=sha1, sha2=sha2, size=len(content), name=name,
                                               file_type=None)
            except IntegrityError:
                return HttpResponseRedirect(reverse('file_already_uploaded'))
            try:
                process_file(sample, content)
            except RedisManagerException:
                sample.delete()
                return HttpResponseRedirect(reverse('no_filter_found'))
            return HttpResponseRedirect(reverse('index'))
    else:  # GET
        form = UploadFileForm()
        return render(request, 'daas_app/upload.html', {'form': form})


def file_already_uploaded(request):
    return render(request, 'daas_app/file_already_uploaded.html')


def no_filter_found(request):
    return render(request, 'daas_app/no_filter_found.html')


class SetResult(APIView):
    def post(self, request):
        result = ast.literal_eval(request.POST['result'])
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        timed_out = result['statistics']['timed_out']
        output = result['statistics']['output']
        decompiled = result['statistics']['decompiled']
        zip = result['zip']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            Statistics.objects.filter(sample=sample).delete()
            statistics = Statistics.objects.create(timeout=timeout, elapsed_time=elapsed_time,
                                                   exit_status=exit_status, timed_out=timed_out,
                                                   output=output, zip_result=zip, decompiled=decompiled,
                                                   decompiler=decompiler, version=version, sample=sample)
            statistics.save()
        return Response({'message': 'ok'})


# Do not use this function as a view. Use it in other views.
def download(file_content, filename, content_type, extension='.daas'):
    filename += extension
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename  # force browser to download file
    response.write(file_content)
    return response


def download_source_code(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    file_content = sample.statistics.zip_result
    return download(file_content, sample.name, "application/x-zip-compressed", extension='.zip')


def download_sample(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    # With the following 'if' nobody will be allowed to download samples if the config say so,
    # even if they manually craft a download url.
    file_content = sample.data if ALLOW_SAMPLE_DOWNLOAD else b''
    return download(file_content, sample.name, "application/octet-stream")


def cancel_job(request, redis_job_pk):
    RedisJob.objects.get(pk=redis_job_pk).cancel()
    return HttpResponseRedirect(reverse_lazy('index'))
