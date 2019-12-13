import requests


def send_metadata(api_url, result):
    requests.post(api_url, {'metadata': str(result)})
