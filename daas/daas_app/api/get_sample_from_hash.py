from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..models import Sample
from ..serializers import SampleSerializer


class GetSampleFromHashAPIView(APIView):
    def get(self, request, hash):
        try:
            sample = Sample.objects.get_sample_with_hash(hash)
        except Sample.DoesNotExist:
            response = Response({'message': 'Sample dos not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SampleSerializer(sample, context={'request': request})
            response = Response(serializer.data, status=status.HTTP_200_OK)
        return response
