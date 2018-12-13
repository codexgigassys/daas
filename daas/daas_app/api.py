from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib

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


class GetSamplesFromHash(AbstractSampleAPIView):
    def post(self, request):
        md5s = self.request.POST.get('md5', [])
        sha1s = self.request.POST.get('sha1', [])
        sha2s = self.request.POST.get('sha2', [])
        return self.serialized_response(Sample.objects.with_hash_in(md5s, sha1s, sha2s), request)


class GetSamplesFromFileType(AbstractSampleAPIView):
    def get(self, request):
        file_type = self.request.query_params.get('file_type').split(',')
        return self.serialized_response(Sample.objects.with_file_type(file_type), request)


class GetSamplesWithSizeBetween(AbstractSampleAPIView):
    def get(self, request):
        lower_size = self.request.query_params.get('lower_size').split(',')
        top_size = self.request.query_params.get('top_size').split(',')
        return self.serialized_response(Sample.objects.with_size_between(lower_size, top_size), request)


class UploadAPI(AbstractResultAPIView):
    def post(self, request):
        name = self.request.POST.get('name')
        content = self.request.POST.get('content')
        reprocessing = self.request.POST.get('reprocess', False)
        upload_file(name, content, reprocessing)
        if reprocessing:
            CallbackManager().add_url(self.request.POST.get('callback'), hashlib.sha1(content).hexdigest())
        else:
            CallbackManager().call(self.request.POST.get('callback'), hashlib.sha1(content).hexdigest())


class ReprocessAPI(AbstractResultAPIView):
    def post(self, request):
        md5s = self.request.POST.get('md5', [])
        sha1s = self.request.POST.get('sha1', [])
        sha2s = self.request.POST.get('sha2', [])
        force_reprocess = self.request.POST.get('force_reprocess').lower() == 'true'

        samples = Sample.objects.with_hash_in(md5s, sha1s, sha2s)
        if not force_reprocess:
            for sample in samples.processed_with_current_decompiler_version():
                CallbackManager().call(self.request.POST.get('callback'), sample.sha1)
            samples = samples.processed_with_old_decompiler_version()

        for sample in samples:
            CallbackManager().add_url(self.request.POST.get('callback'), sample.sha1)
            reprocess(sample)
