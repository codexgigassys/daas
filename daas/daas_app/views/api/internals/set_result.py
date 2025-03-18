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
        logging.info(
            f'processing result for sample {result["statistics"]["sha1"]} (sha1)')
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        result = Result()
        result.sample = sample
        result.timeout = result['statistics']['timeout']
        result.elapsed_time = result['statistics']['elapsed_time']
        result.exit_status = result['statistics']['exit_status']
        result.status = self._determine_result_status(result['statistics'])
        result.output = result['statistics']['output']
        result.seaweed_result_id = result['source_code']['seaweedfs_result_id']
        result.extension = result['source_code']['extension']
        result.decompiler = result['statistics']['decompiler']
        result.version = result['statistics']['version']
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
