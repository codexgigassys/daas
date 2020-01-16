from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import logging

from ...utils.callback_manager import CallbackManager
from ...serializers import SampleSerializer
from ...utils.lists import recursive_flatten


class CreateSampleView(APIView):
    @swagger_auto_schema(
        operation_id='create_sample',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sample': openapi.Schema(type=openapi.TYPE_OBJECT,
                                         description='Serializable sample metadata.'),  # FIXME document it better
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
        force_reprocess = request.data.get('force_reprocess', False)
        callback = request.data.get('callback')
        sample_data = request.data.get('sample')
        samples = self.serialize_sample(sample_data)

        if callback:
            pass  # todo do callback magic here
        return Response(status=status.HTTP_200_OK, data={'non_zip_samples': len(samples)})

    def serialize_sample(self, sample_data):
        if not sample_data:  # No sample to serialize (either sample not found by meta_extractor or subfiles of an empty zip)
            samples = []
        elif sample_data['file_type'] == 'zip':  # Zip sample
            samples = [self.serialize_sample(subfile) for subfile in sample_data['subfiles']]
        else:  # Non-zip sample
            sample_serializer = SampleSerializer(data=sample_data)
            if sample_serializer.is_valid():
                sample = sample_serializer.save()
                samples = [sample]
            else:
                logging.info(f'Create sample: serializer is not valid: {sample_serializer.data=}')
        return recursive_flatten(samples)
