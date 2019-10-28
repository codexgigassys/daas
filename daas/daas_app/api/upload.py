from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import hashlib
import logging

from ..utils.upload_file import upload_file
from ..utils.callback_manager import CallbackManager
from ..utils.classifier import ClassifierError


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
        return Response(status=status.HTTP_202_ACCEPTED)
