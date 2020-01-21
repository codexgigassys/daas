from django.contrib.auth.decorators import login_required, permission_required
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ...models import Sample
from ...view_utils import download


@swagger_auto_schema(
    method='get',
    operation_id='download_source_code',
    manual_parameters=[
        openapi.Parameter(
            name='sample_id', in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        status.HTTP_200_OK: openapi.Response(
            description='Sample found.',
            schema=openapi.Schema(format='application/x-zip-compressed', type=openapi.TYPE_FILE)
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description='There is no sample with the given ID.',
        )
    }
)
@login_required
@api_view(["GET"])
@permission_required('download_source_code_permission')
def download_source_code_view(request, sample_id):
    logging.info(f'Downloading source code: {sample_id=}')
    sample = get_object_or_404(Sample, id=sample_id)
    zipped_source_code = sample.result.compressed_source_code.tobytes()
    return download(zipped_source_code, sample.name, "application/x-zip-compressed", extension=sample.result.extension)
