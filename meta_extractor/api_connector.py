import requests
import logging


def send_result(api_url, result):
    logging.error(result)
    response = requests.post(f'http://{api_url}/internal/api/create_sample', json=result)
    assert response.status_code == 201
    return response
