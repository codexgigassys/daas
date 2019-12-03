import requests


def send_generic_reuslt(api_url, result):
    requests.post(api_url, {'result': str(result)})
