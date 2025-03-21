from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.request import Request
import json

from ....utils.charts import (samples_per_size, samples_per_elapsed_time, samples_per_type, samples_per_upload_date,
                              samples_per_process_date, samples_per_status_for_file_type)


def response_as_json(data: dict) -> HttpResponse:
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200) -> HttpResponse:
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string: str = "error", code: int = 500, **kwargs) -> HttpResponse:
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


class SamplesPerSizeData(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        data = samples_per_size()
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)


class SamplesPerElapsedTimeData(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        data = samples_per_elapsed_time()
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)


class SamplesPerTypeData(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        data = samples_per_type()
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)


class SamplesPerUploadDateData(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        data = samples_per_upload_date()
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)


class SamplesPerProcessDateData(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        data = samples_per_process_date()
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)


class SamplesPerStatusForFileTypeData(APIView):
    def get(self, request: Request, file_type, *args, **kwargs) -> JsonResponse:
        data = samples_per_status_for_file_type(file_type)
        return JsonResponse(json.loads(data.dump_options_with_quotes())) if data is not None else JsonResponse(None)
