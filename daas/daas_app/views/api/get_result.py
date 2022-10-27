from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from ...models import Sample
from ...serializers import SampleSerializer


class GetResultAPIView(APIView):
    @swagger_auto_schema(
        operation_id='get_result',
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
    def get(self, request: Request) -> Response:
        hashes = request.data.getlist('hashes', [])
        samples = Sample.objects.with_hash_in(hashes)
        force_reprocess = bool(request.data.get('force_reprocess', False))
        callback = request.data.get('callback', None)

        submitted_samples = self.reprocess(samples=samples, force_reprocess=force_reprocess, callback=callback)

        return Response({'submitted_samples': submitted_samples}, status.HTTP_202_ACCEPTED)
