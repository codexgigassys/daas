from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
import ast
import hashlib
from django.urls import reverse_lazy
from django.db import IntegrityError
import logging
from django.db import transaction
import json
from django.db.models import Max

from .forms import UploadFileForm
from .utils.redis_manager import RedisManager, RedisManagerException
from .config import SAVE_SAMPLES, ALLOW_SAMPLE_DOWNLOAD
from .models import Sample, Statistics, RedisJob
from .utils.charts.bar_chart_json_generator import generate_stacked_bar_chart
from .utils.charts.pie_chart_json_generator import generate_pie_chart
from .utils.charts.data_zoom_chart_json_generator import generate_zoom_chart
from .utils.configuration_manager import ConfigurationManager


class IndexView(generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class StatisticsView(generic.View):
    """ Decompiled samples per size """
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        charts = [{'content': samples_per_size_chart(), 'name': 'samples_per_size_chart', 'title': 'Samples per size', 'echart_required_chart': 'bar', 'full_width': True},
                  {'content': samples_per_elapsed_time_chart(), 'name': 'samples_per_elapsed_time_chart', 'title': 'Samples per elapsed time', 'echart_required_chart': 'bar', 'full_width': True},
                  {'content': samples_per_type_chart(), 'name': 'samples_per_type_chart', 'title': 'Samples per type', 'echart_required_chart': 'pie', 'full_width': True},
                  {'content': samples_per_upload_date_chart(), 'name': 'samples_per_upload_date_chart',
                   'title': 'Samples per upload date', 'full_width': True, 'echart_required_chart': 'pie'},
                  {'content': samples_per_process_date(), 'name': 'samples_per_process_date',
                   'title': 'Samples per process date', 'full_width': True, 'echart_required_chart': 'pie'}]
        for file_type in ConfigurationManager().get_identifiers():
            charts.append({'content': samples_per_decompilation_status_chart(file_type),
                           'name': 'samples_per_size_chart_%s' % file_type,
                           'title': '%s samples by status' % ConfigurationManager().get_sample_type(file_type),
                           'echart_required_chart': 'pie',
                           'echart_theme': 'infographic'})
        return render(request, 'daas_app/statistics.html', {'charts': charts})


def samples_per_size_chart():
    ranges = [(0, 30), (30, 60), (60, 90), (90, 120), (120, 150), (150, 180), (180, 1000), (1000, 2**30)]
    samples_by_size_range = [Sample.objects.with_size_between(size_from*1024, size_to*1024 - 1) for (size_from, size_to) in ranges]
    y_axis_legend = ["< 30kb", "30-59kb", "60-89kb", "90-119kb", "120-149kb", "150-179kb", "180-1000kb", "> 1000kb"]
    chart = generate_stacked_bar_chart(y_axis_legend, samples_by_size_range)
    return json.dumps(chart)


def samples_per_elapsed_time_chart():
    max_elapsed_time = Statistics.objects.filter(decompiled=True).aggregate(Max('elapsed_time'))['elapsed_time__max']
    # this would limit the number items on X axis to 30 at most.
    # If step is 2, X axis items would be: 1-2, 3-4, 5-6, ....
    # If step is 3: 1-3, 4-6, 7-9, ...
    # If step is 4: 1-4, 5-8, 8-11, ...
    steep = max(max_elapsed_time / 30, 2)
    # Generate the above mentioned ranges based on the steep, from zero to the maximum elapsed time.
    ranges = [(i, i + (steep - 1)) for i in range(0, max_elapsed_time, steep)]
    samples_by_elapsed_time_range = [Sample.objects.with_elapsed_time_between(from_, to) for (from_, to) in ranges]
    y_axis_legend = ["%s-%s" % element for element in ranges]  # 1-2, 3-4, 5-6, ...
    chart = generate_stacked_bar_chart(y_axis_legend, samples_by_elapsed_time_range)
    return json.dumps(chart)


def samples_per_type_chart():
    chart = generate_pie_chart(Sample.objects.classify_by_file_type(count=True))
    return json.dumps(chart)


def samples_per_decompilation_status_chart(file_type):
    samples_of_a_given_type_by_status = {'Decompiled': Sample.objects.decompiled().filter(file_type=file_type).count(),
                                         'Time out': Sample.objects.timed_out().filter(file_type=file_type).count(),
                                         'Failed': Sample.objects.failed().filter(file_type=file_type).count()}
    chart = generate_pie_chart(samples_of_a_given_type_by_status)
    return json.dumps(chart)


def samples_per_upload_date_chart():
    counts = Sample.objects.samples_per_upload_date().classify_by_file_type()
    chart = generate_zoom_chart(counts)
    return json.dumps(chart)


def samples_per_process_date():
    counts = Sample.objects.samples_per_process_date().classify_by_file_type()
    chart = generate_zoom_chart(counts)
    return json.dumps(chart)


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
            except RedisManagerException: # fix it!
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
