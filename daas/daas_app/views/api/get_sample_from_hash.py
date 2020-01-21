from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...models import Sample
from ...serializers import SampleSerializer


class GetSampleFromHashAPIView(APIView):
    @swagger_auto_schema(
        operation_id='get_sample',
        manual_parameters=[
            openapi.Parameter(
                name='hash', in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Hash. May be either MD5, SHA1 or SHA2.",
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Sample found.',
                schema=SampleSerializer()
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='There are no samples with the given hash.',
            )
        }
    )
    def get(self, request, hash):
        try:
            sample = Sample.objects.get_sample_with_hash(hash)
        except Sample.DoesNotExist:
            response = Response({'message': 'Sample dos not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SampleSerializer(sample, context={'request': request})
            response = Response(serializer.data, status=status.HTTP_200_OK)
        return response
