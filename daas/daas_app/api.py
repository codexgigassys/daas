from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
import logging

from .models import Sample
from .utils.reprocess import reprocess
from .serializers import SampleWithoutDataSerializer, SampleSerializer, ResultSerializer
from .utils.upload_file import upload_file
from .utils.callback_manager import CallbackManager
from .utils.classifier import ClassifierError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def get_token(request):
    username = request.POST['username']
    password = request.POST['password']
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)


class AbstractSampleAPIView(APIView):
    def serialized_response(self, samples, request):
        """
        :param samples: Sample queryset
        :return: Response that should return every subclass of this one
        """
        serializer = SampleSerializer(samples, many=True, context={'request': request})
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


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        uploaded_file = request.data.get('file')
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback', None)
        logging.info('Upload API. File name: %s. File content length: %s. Force process: %s. Callback: %s.' % (uploaded_file.name, uploaded_file.size, force_reprocess, callback))
        try:
            _, should_process = upload_file(uploaded_file.name, uploaded_file.read(), force_reprocess)
        # Temporary fix. This will be refactored soon.
        except ClassifierError:
            logging.info('No valid classifier for file.')
        else:
            if callback is not None:
                if should_process:
                    CallbackManager().add_url(callback, hashlib.sha1(content).hexdigest())
                else:
                    CallbackManager().call(callback, hashlib.sha1(content).hexdigest())
        logging.info('File uploaded. Returning status 202.')
        return Response(status=202)


class ReprocessAPIView(APIView):
    def post(self, request):
        md5s = request.data.get('md5', [])
        sha1s = request.data.get('sha1', [])
        sha2s = request.data.get('sha2', [])
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback', None)
        logging.info('Reprocess API. md5s=%s, sha1s=%s, sha2s=%s. Force reprocess: %s. Callback: %s' % (md5s, sha1s, sha2s, force_reprocess, callback))
        samples = Sample.objects.with_hash_in(md5s, sha1s, sha2s)
        if not force_reprocess:
            # Return data for samples processed with the latest decompiler.
            for sample in samples.processed_with_current_decompiler_version():
                CallbackManager().call(request.POST.get('callback'), sample.sha1)
            samples = samples.processed_with_old_decompiler_version()

        # Reprocess and add a callback for samples processed with old decompilers.
        for sample in samples:
            CallbackManager().add_url(callback, sample.sha1)
            reprocess(sample, force_reprocess=force_reprocess)
        logging.info('Files sent for reprocess (if needed or forced). Returning status 202.')
        return Response(status=202)
