from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..utils.callback_manager import CallbackManager
from ..utils.new_files import create_and_upload_file


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    @swagger_auto_schema(
        operation_id='upload',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE),
                'zip_password': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Zip password. Leave this field empty or set it to null or an empty string if you are uploading a non-zip file or a non-protected zip.'),
                'force_reprocess': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                  description='To reprocess the file regardless the decompiler version.',
                                                  default=False),
                'callback': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Callback URL.')
            },
            required=['file']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing file parameter.',
            ),
            status.HTTP_202_ACCEPTED: openapi.Response(
                description='File uploaded successfully.',
            )
        }
    )
    def post(self, request):
        uploaded_file = request.data.get('file')
        zip_password = bytes(request.data.get('zip_password', '').encode('utf-8'))
        if not uploaded_file:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            file = create_and_upload_file(file_name=uploaded_file.name,
                                          content=uploaded_file.read(),
                                          force_reprocess=request.data.get('force_reprocess', False),
                                          zip_password=zip_password)

            # Callback
            callback = request.data.get('callback', None)
            if file and callback:
                if file.will_be_processed:
                    CallbackManager().add_url(callback, file.sha1)
                else:
                    # fixme: it may be better to return the data instead of calling sending a request
                    # without answering this. The current behaviour may cause race conditions on programs
                    # that integrate with daas.
                    CallbackManager().call(callback, file.sha1)
            response = Response(status=status.HTTP_202_ACCEPTED)
        return response
