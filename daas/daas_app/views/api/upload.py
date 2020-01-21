from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pyseaweed import WeedFS

from ...utils.task_manager import TaskManager


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
    def post(self, request: Request) -> Response:
        file = request.data.get('file')
        external_url = request.data.get('file_url')
        file_name = request.data.get('file_name')
        zip_password = request.data.get('zip_password', '')
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback')

        response = Response(status=status.HTTP_202_ACCEPTED)

        if file:
            # Upload the file and send the file ID on seaweedfs
            seaweedfs = WeedFS('seaweedfs_master', 9333)
            seaweedfs_file_id = seaweedfs.upload_file(stream=file.read(),
                                                      name=file_name if file_name else file.name)
            TaskManager().submit_url_for_metadata_extractor(zip_password=zip_password,
                                                            force_reprocess=force_reprocess,
                                                            callback=callback,
                                                            seaweedfs_file_id=seaweedfs_file_id,
                                                            file_name=file_name)
        elif external_url:
            # Send the url to download the file on the metadata extractor to avoid an overflow of the API if
            # lots of files are sent at the same time
            TaskManager().submit_url_for_metadata_extractor(zip_password=zip_password,
                                                            force_reprocess=force_reprocess,
                                                            callback=callback,
                                                            external_url=external_url,
                                                            file_name=file_name)
        else:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
        return response
