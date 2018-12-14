from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser

from .models import Sample
from .utils.reprocess import reprocess
from .serializers import SampleWithoutDataSerializer, SampleSerializer, ResultSerializer
from .utils.upload_file import upload_file
from .utils.callback_manager import CallbackManager


class AbstractSampleAPIView(APIView):
    def serialized_response(self, samples, request):
        """
        :param samples: Sample queryset
        :return: Response that should return every subclass of this one
        """
        serializer = SampleSerializer(samples, many=True, context={'request': request})
        return Response(serializer.data)


class AbstractResultAPIView(APIView):
    def serialized_response(self, results, request):
        """
        :param results: Result queryset
        :return: Response that should return every subclass of this one
        """
        serializer = SampleSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)


class GetSamplesFromHashAPIView(AbstractSampleAPIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        md5s = request.data.get('md5', [])
        sha1s = request.data.get('sha1', [])
        sha2s = request.data.get('sha2', [])
        return self.serialized_response(Sample.objects.with_hash_in(md5s, sha1s, sha2s), request)


class GetSamplesFromFileTypeAPIView(AbstractSampleAPIView):
    def get(self, request):
        file_types = request.query_params.get('file_type').split(',')
        return self.serialized_response(Sample.objects.with_file_type_in(file_types), request)


class GetSamplesWithSizeBetweenAPIView(AbstractSampleAPIView):
    def get(self, request):
        lower_size = request.query_params.get('lower_size')
        top_size = request.query_params.get('top_size')
        return self.serialized_response(Sample.objects.with_size_between(lower_size, top_size), request)


class UploadAPIView(AbstractResultAPIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        name = request.POST.get('name')
        content = request.POST.get('content')
        reprocessing = request.POST.get('reprocess', False)
        upload_file(name, content, reprocessing)
        if reprocessing:
            CallbackManager().add_url(request.POST.get('callback'), hashlib.sha1(content).hexdigest())
        else:
            CallbackManager().call(request.POST.get('callback'), hashlib.sha1(content).hexdigest())


class ReprocessAPIView(AbstractResultAPIView):
    def post(self, request):
        md5s = request.POST.get('md5', [])
        sha1s = request.POST.get('sha1', [])
        sha2s = request.POST.get('sha2', [])
        force_reprocess = request.POST.get('force_reprocess').lower() == 'true'

        samples = Sample.objects.with_hash_in(md5s, sha1s, sha2s)
        if not force_reprocess:
            for sample in samples.processed_with_current_decompiler_version():
                CallbackManager().call(request.POST.get('callback'), sample.sha1)
            samples = samples.processed_with_old_decompiler_version()

        for sample in samples:
            CallbackManager().add_url(request.POST.get('callback'), sample.sha1)
            reprocess(sample)
