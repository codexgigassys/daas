from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
import ast
import logging
from typing import Dict, Any

from ....models import Sample, Result
from ....utils.status import ResultStatus
from ....utils.callback_manager import CallbackManager


class SetResultApiView(APIView):
    def post(self, request: Request) -> Response:
        logging.debug(f'{request.data=}')
        # fixme: use a serializer for this
        result = ast.literal_eval(request.POST['result'])
        logging.error(f'processing result for sample {result["statistics"]["sha1"]} (sha1)')
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        status = self._determine_result_status(result['statistics'])
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

        CallbackManager().send_callbacks(sample.sha1)

        return Response({'message': 'ok'})

    def _determine_result_status(self, statistics: Dict[str, Any]) -> int:
        if statistics['timed_out']:
            status = ResultStatus.TIMED_OUT
        elif statistics['decompiled']:
            status = ResultStatus.SUCCESS
        else:
            status = ResultStatus.FAILED
        return status.value
