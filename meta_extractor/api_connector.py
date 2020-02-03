import requests
import logging
from typing import Dict, Any


def send_result(api_url: str, result: Dict[str, Any]):
    logging.error(result)
    response = requests.post(f'http://{api_url}/internal/api/create_sample', json=result)
    assert response.status_code == 201
    return response
