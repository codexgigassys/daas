from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
import ast
import logging
import json

from .forms import UploadFileForm
from .config import ALLOW_SAMPLE_DOWNLOAD
from .models import Sample, Result, RedisJob
from .utils.upload_file import upload_file
from .utils import classifier
from .utils import result_status
from .utils.charts.chart_cache import ChartCache


class IndexView(generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class StatisticsView(generic.View):
    """ Decompiled samples per size """
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        """
        charts = [{'content': samples_per_size_chart(), 'name': 'samples_per_size_chart', 'title': 'Samples per size', 'echart_required_chart': 'bar', 'full_width': True},
                  {'content': samples_per_elapsed_time_chart(), 'name': 'samples_per_elapsed_time_chart', 'title': 'Samples per elapsed time', 'echart_required_chart': 'bar', 'full_width': True},
                  {'content': samples_per_type_chart(), 'name': 'samples_per_type_chart', 'title': 'Samples per type', 'echart_required_chart': 'pie', 'full_width': True},
                  {'content': samples_per_upload_date_chart(), 'name': 'samples_per_upload_date_chart',
                   'title': 'Samples per upload date', 'full_width': True, 'echart_required_chart': 'pie'},
                  {'content': samples_per_process_date_chart(), 'name': 'samples_per_process_date',
                   'title': 'Samples per process date', 'full_width': True, 'echart_required_chart': 'pie'}]
        for configuration in ConfigurationManager().get_configurations():
            identifier = configuration.identifier
            charts.append({'content': samples_per_decompilation_status_chart(identifier),
                           'name': 'samples_per_size_chart_%s' % identifier,
                           'title': '%s samples by status' % configuration.sample_type,
                           'echart_required_chart': 'pie',
                           'echart_theme': 'infographic'})
        """
        charts = ChartCache().get_charts()
        time_since_last_update = ChartCache().time_since_last_update
        if time_since_last_update < 60:
            time_since_last_update = "%s seconds." % time_since_last_update
        elif time_since_last_update < 3600:
            time_since_last_update = "%s minutes." % int(time_since_last_update / 60)
        elif time_since_last_update < 3600*24:
            time_since_last_update = "%s hours." % int(time_since_last_update / 3600)
        else:
            time_since_last_update = "%s hours." % int(time_since_last_update / (3600 * 24))
        for chart in charts:
            chart['content'] = json.dumps(chart['content'])
        return render(request, 'daas_app/statistics.html', {'charts': charts,
                                                            'time_since_last_update': time_since_last_update})


class SampleDeleteView(generic.edit.DeleteView):
    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'


def reprocess(request, sample_id):
    # If we didn't save the sample, we have no way to decompile it again using this view
    sample = Sample.objects.get(id=sample_id)
    if sample.content_saved():
        logging.debug('Reprocessing sample: %s' % sample_id)
        upload_file(sample.name, sample.data.tobytes(), reprocessing=True)
    else:
        # It's not necessary to return a proper error here, because the URL will not be accessible via GUI
        # if the sample is not saved.
        logging.error('It was not possible to reprocess sample %s because it was not saved.' % sample_id)
    return HttpResponseRedirect(reverse('index'))


def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content = request.FILES['file'].file.read()
            name = request.FILES['file'].name
            try:
                upload_file(name, content)
            except IntegrityError:
                return HttpResponseRedirect(reverse('file_already_uploaded'))
            except classifier.ClassifierError:  # fix it!
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
        status = result_status.TIMED_OUT if result['statistics']['timed_out'] else\
            (result_status.SUCCESS if result['statistics']['decompiled'] else result_status.FAILED)
        output = result['statistics']['output']
        zip = result['zip']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            Result.objects.filter(sample=sample).delete()
            statistics = Result.objects.create(timeout=timeout, elapsed_time=elapsed_time, exit_status=exit_status,
                                               status=status.value, output=output, zip_result=zip,
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
