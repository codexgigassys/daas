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
        # To Do: refactor this method
        logging.debug(f'{request.data=}')
        # fixme: use a serializer for this
        result = ast.literal_eval(request.POST['result'])
        logging.error(
            f'processing result for sample {result["statistics"]["sha1"]} (sha1)')
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        status = self._determine_result_status(result['statistics'])
        output = result['statistics']['output']
        seaweed_result_id = result['source_code']['seaweedfs_result_id']
        extension = result['source_code']['extension']
        decompiler = result['statistics']['decompiler']
        version = result['statistics']['version']
        with transaction.atomic():
            # result = Result.objects.filter(sample=sample)
            result = Result()
            result.sample = sample
            # "compressed_source_code=file" was extracted of the Result creation
            result.timeout = timeout
            result.elapsed_time = elapsed_time
            result.exit_status = exit_status
            result.status = status
            result.output = output
            result.seaweed_result_id = seaweed_result_id
            result.extension = extension
            result.decompiler = decompiler
            result.version = version
            result.save()

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
