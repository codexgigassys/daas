from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
import ast
import logging

from ...models import Sample, Result
from ...utils import result_status


class SetResultApiView(APIView):
    def post(self, request):
        result = ast.literal_eval(request.POST['result'])
        logging.info('processing result for sample %s (sha1)' % result['statistics']['sha1'])
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        status = result_status.TIMED_OUT if result['statistics']['timed_out'] else\
            (result_status.SUCCESS if result['statistics']['decompiled'] else result_status.FAILED)
        output = result['statistics']['output']
        file = result['source_code']['file']
        extension = result['source_code']['extension']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            Result.objects.filter(sample=sample).delete()
            result = Result.objects.create(timeout=timeout, elapsed_time=elapsed_time,
                                           exit_status=exit_status, status=status, output=output,
                                           compressed_source_code=file, extension=extension, decompiler=decompiler, version=version,
                                           sample=sample)
            result.save()
        return Response({'message': 'ok'})
