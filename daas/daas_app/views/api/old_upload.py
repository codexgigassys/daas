from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests

from ...utils.callback_manager import CallbackManager
from ...utils.new_files import create_and_upload_file


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
        if file_url := request.data.get('file_url'):
            download_file_reply = requests.get(file_url)
            try:
                download_file_reply.raise_for_status()
            except requests.exceptions.HTTPError():
                pass  # the response is going be "400: bad request", because content and file_name will be unset. Therefore, we do not need to do anything with this exception.
            else:
                content = download_file_reply.content
                file_name = request.data.get('file_name')
        else:
            if uploaded_file := request.data.get('file'):
                file_name, content = uploaded_file.name, uploaded_file.read()

        if file_name and content:
            zip_password = bytes(request.data.get('zip_password', '').encode('utf-8'))

            file = create_and_upload_file(file_name=file_name,
                                          content=content,
                                          force_reprocess=request.data.get('force_reprocess', False),
                                          zip_password=zip_password)

            # Callback
            callback = request.data.get('callback', None)
            if file and callback:
                if file.will_be_processed:
                    CallbackManager().add_url(callback, file.sha1)
                else:
                    CallbackManager().call(callback, file.sha1)
            response = Response(status=status.HTTP_202_ACCEPTED)
        else:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
        return response
