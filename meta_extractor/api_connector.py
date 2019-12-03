import requests


class DaaSAPIConnector:
    def __init__(self, api_base_url):
        self.base_url = api_base_url

    def send_result(self, result):
        return requests.post(f'http://{self.base_url}/internal/api/set_result', {'result': str(result)})
