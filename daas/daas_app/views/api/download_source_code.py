from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.http import HttpResponse

from ...models import Sample, Result
from ...view_utils import download


class DownloadSourceCodeAPIView(APIView):
    @swagger_auto_schema(
        operation_id='download_source_code',
        manual_parameters=[
            openapi.Parameter(
                name='hash', in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Sample and result found.',
                schema=openapi.Schema(format='application/x-zip-compressed', type=openapi.TYPE_FILE)
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='There is no sample with the given Hash or it has not result.',
            )
        }
    )
    def get(self, request: Request, hash: str) -> HttpResponse:
        logging.info(f'Downloading source code: {hash=}')
        sample = get_object_or_404(Sample, sha1=hash)
        result = get_object_or_404(Result, sample=sample)
        zipped_source_code = result.compressed_source_code
        # zipped_source_code = result.compressed_source_code.tobytes()
        return download(zipped_source_code, sample.file_name, "application/x-zip-compressed",
                        extension=sample.last_result.extension)
