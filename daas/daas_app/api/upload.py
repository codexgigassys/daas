from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from ..utils.callback_manager import CallbackManager
from ..utils.new_files import create_and_upload_file


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        uploaded_file = request.data.get('file')
        zip_password = bytes(request.data.get('zip_password', '').encode('utf-8'))
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
        return Response(status=status.HTTP_202_ACCEPTED)
