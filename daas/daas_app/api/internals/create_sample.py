from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests

from ...utils.callback_manager import CallbackManager
from ...serializers import SampleSerializer


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    @swagger_auto_schema(
        operation_id='upload',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE,
                                       description='File content. Set this parameter or "file_url", not both.'),
                'file_url': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Url to download the file. Set this parameter or "file", not both.'),
                'file_name': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Parameter to set the file name in case you chose to use "file_url" instead of "file".'),
                'zip_password': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Zip password. Leave this field empty or set it to null or an empty string if you are uploading a non-zip file or a non-protected zip.'),
                'force_reprocess': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                  description='To reprocess the file regardless the decompiler version, if it was already processed.',
                                                  default=False),
                'callback': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Callback URL.')
            }
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing file parameter or invalid file_url (if not omitted).',
            ),
            status.HTTP_202_ACCEPTED: openapi.Response(
                description='File uploaded successfully.',
            )
        }
    )
    def post(self, request):
        # Get parameters
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback')
        try:
            sample_data = request.data['sample']
        except KeyError:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            SampleSerializer(data=sample_data)

        if callback:
            pass  # todo do callback magic here
        return response

    def serialize_sample(self, sample_data):
        samples = []
        if sample_data['file_type'] == 'zip':
            for subfile in sample_data['subfiles']:
                if subfile['file_type'] == 'zip':
                    pass
                else:
                    return self.serialize_sample
        else:
            samples = [SampleSerializer(data=sample_data)]
        return samples

