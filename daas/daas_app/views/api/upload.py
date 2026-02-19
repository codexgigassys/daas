from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..utils.mixins import UploadMixin
from ...models import Sample


class UploadAPIView(UploadMixin, APIView):
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
                'sha1': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Parameter to set the sha1 hash'),
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
                description='You should specify file or file_url.',
            ),
            status.HTTP_202_ACCEPTED: openapi.Response(
                description='File uploaded successfully.',
            )
        }
    )
    def post(self, request: Request) -> Response:
        successfully_uploaded = False
        sha1 = request.data.get('sha1')
        try:
            Sample.objects.get(sha1=sha1)
        except Sample.DoesNotExist:
            successfully_uploaded = self.upload(file=request.data.get('file'),
                                                external_url=request.data.get(
                                                    'file_url'),
                                                file_name=request.data.get(
                                                    'file_name'),
                                                zip_password=request.data.get(
                                                    'zip_password', ''),
                                                force_reprocess=request.data.get(
                                                    'force_reprocess', False),
                                                callback=request.data.get('callback'))
        return Response(status=status.HTTP_202_ACCEPTED if successfully_uploaded else status.HTTP_400_BAD_REQUEST)
