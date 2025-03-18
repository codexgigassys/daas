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
        result_new = Result()
        result_new.sample = sample
        result_new.timeout = result['statistics']['timeout']
        result_new.elapsed_time = result['statistics']['elapsed_time']
        result_new.exit_status = result['statistics']['exit_status']
        result_new.status = self._determine_result_status(result['statistics'])
        result_new.output = result['statistics']['output']
        result_new.seaweed_result_id = result['source_code']['seaweedfs_result_id']
        result_new.extension = result['source_code']['extension']
        result_new.decompiler = result['statistics']['decompiler']
        result_new.version = result['statistics']['version']
        result_new.save()

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
