from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .utils.reprocess import reprocess


class GetSamplesFromHash(APIView):
    def post(self, request):
        md5s = self.request.POST.get('md5', [])
        sha1s = self.request.POST.get('sha1', [])
        sha2s = self.request.POST.get('sha2', [])

        Sample.objects.with_hash_in(md5s, sha1s, sha2s)
        return Response('serializar!')


class GetSamplesFromFileType(APIView):
    def get(self, request):
        file_type = self.request.query_params.get('file_type').split(',')
        Sample.objects.with_file_type(file_type)
        return Response('serializar!')


class GetSamplesWithSizeBetween(APIView):
    def get(self, request):
        lower_size = self.request.query_params.get('lower_size').split(',')
        top_size = self.request.query_params.get('top_size').split(',')
        Sample.objects.with_size_between(lower_size, top_size)
        return Response('serializar!')


class ReprocessAPI(APIView):
    def post(self, request):
        md5s = self.request.POST.get('md5', [])
        sha1s = self.request.POST.get('sha1', [])
        sha2s = self.request.POST.get('sha2', [])
        callback = self.request.POST.get('callback')
        force_reprocess = self.request.POST.get('force_reprocess').lower() == 'true'

        samples = Sample.objects.with_hash_in(md5s, sha1s, sha2s)
        if not force_reprocess:
            samples = samples.processed_with_old_decompiler_version()

        for sample in samples:
            reprocess(sample)

        if callback is not None:
            return Response('serializado de decompilados!')
