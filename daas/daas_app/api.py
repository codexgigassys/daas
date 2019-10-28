from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
import logging
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
from rest_framework import status

from .models import Sample
from .utils.reprocess import reprocess
from .serializers import SampleWithoutDataSerializer, SampleSerializer, ResultSerializer
from .utils.upload_file import upload_file
from .utils.callback_manager import CallbackManager
from .utils.classifier import ClassifierError


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
    return Response({'token': token.key}, status=status.HTTP_200_OK)


class GetSampleFromHashAPIView(APIView):
    parser_classes = (JSONParser,)

    def get(self, request, hash):
        try:
            sample = Sample.objects.get_sample_with_hash(hash)
        except Sample.DoesNotExist:
            response = Response({'message': 'Sample dos not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SampleSerializer(sample, context={'request': request})
            response = Response(serializer.data, status=status.HTTP_200_OK)
        return response


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        uploaded_file = request.data.get('file')
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback', None)
        zip_password = bytes(request.data.get('zip_password', '').encode('utf-8'))
        logging.info('Upload API. File name: %s. File content length: %s. Force process: %s. Callback: %s.' % (uploaded_file.name, uploaded_file.size, force_reprocess, callback))
        content = uploaded_file.read()
        try:
            _, should_process = upload_file(uploaded_file.name, content, force_reprocess, zip_password=zip_password)
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
        return Response(status=status.HTTP_202_ACCEPTED)


class ReprocessAPIView(APIView):
    def post(self, request):
        hashes = request.data.get('hashes', [])
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback', None)
        logging.info(f'Reprocess API. Force reprocess: {force_reprocess}. Callback: {callback}. Hashes: {hashes}')
        samples = Sample.objects.with_hash_in(hashes)
        if not force_reprocess:
            # Return data for samples processed with the latest decompiler.
            for sample in samples.processed_with_current_decompiler_version():
                CallbackManager().call(callback, sample.sha1)
            samples = samples.processed_with_old_decompiler_version()

        # Reprocess and add a callback for samples processed with old decompilers.
        for sample in samples:
            CallbackManager().add_url(callback, sample.sha1)
            reprocess(sample, force_reprocess=force_reprocess)

        logging.info('Files sent for reprocess (if needed or forced). Returning status 202.')
        return Response(status=status.HTTP_202_ACCEPTED)
