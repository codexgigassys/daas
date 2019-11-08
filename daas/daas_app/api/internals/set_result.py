from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest
import ast
import logging

from ...models import Sample, Result
from ...utils.status import ResultStatus


class SetResultApiView(APIView):
    def post(self, request: HttpRequest) -> Response:
        # fixme: use a serializer for this
        result = ast.literal_eval(request.POST['result'])
        logging.info('processing result for sample %s (sha1)' % result['statistics']['sha1'])
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        status = ResultStatus.TIMED_OUT.value if result['statistics']['timed_out'] else \
            (ResultStatus.SUCCESS if result['statistics']['decompiled'] else ResultStatus.FAILED).value
        output = result['statistics']['output']
        file = result['source_code']['file']
        extension = result['source_code']['extension']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            Result.objects.filter(sample=sample).delete()
            Result.objects.create(timeout=timeout, elapsed_time=elapsed_time, exit_status=exit_status,
                                  status=status, output=output, compressed_source_code=file,
                                  extension=extension, decompiler=decompiler, version=version, sample=sample)
        return Response({'message': 'ok'})
