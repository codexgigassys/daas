from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..utils.mixins import ReprocessMixin
from ...models import Sample


class ReprocessAPIView(ReprocessMixin, APIView):
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
        hashes = request.data.getlist('hashes', [])
        samples = Sample.objects.with_hash_in(hashes)
        force_reprocess = bool(request.data.get('force_reprocess', False))
        callback = request.data.get('callback', None)

        submitted_samples = self.reprocess(samples=samples, force_reprocess=force_reprocess, callback=callback)

        return Response({'submitted_samples': submitted_samples}, status.HTTP_202_ACCEPTED)
