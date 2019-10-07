from django.http import HttpResponse
from rest_framework.views import APIView
import json

from ..utils.charts import (samples_per_size, samples_per_elapsed_time, samples_per_type,
                            samples_per_upload_date, samples_per_process_date, samples_per_status_for_file_type)


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
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
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_size().dump_options_with_quotes()))


class SamplesPerElapsedTimeData(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_elapsed_time().dump_options_with_quotes()))


class SamplesPerTypeData(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_type().dump_options_with_quotes()))


class SamplesPerUploadDateData(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_upload_date().dump_options_with_quotes()))


class SamplesPerProcessDateData(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_process_date().dump_options_with_quotes()))


class SamplesPerStatusForFileTypeData(APIView):
    def get(self, request, file_type, *args, **kwargs):
        return JsonResponse(json.loads(samples_per_status_for_file_type(file_type).dump_options_with_quotes()))
