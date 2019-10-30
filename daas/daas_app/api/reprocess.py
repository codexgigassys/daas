from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Sample
from ..utils.reprocess import reprocess
from ..utils.callback_manager import CallbackManager


class ReprocessAPIView(APIView):
    @swagger_auto_schema(
        operation_id='reprocess',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'hashes': openapi.Schema(type=openapi.TYPE_ARRAY,
                                         items=openapi.Items(type=openapi.TYPE_STRING),
                                         default=[]),
                'force_reprocess': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                  description='To reprocess the file regardless the decompiler version.',
                                                  default=False),
                'callback': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Callback URL.')
            },
            required=[]
        ),
        responses={
            status.HTTP_202_ACCEPTED: openapi.Response(
                description='Request accepted. Files will be reprocessed soon.',
            )
        }
    )
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

        return Response(status=status.HTTP_202_ACCEPTED)
