import logging
from typing import Dict, Any

from ..http_retry import make_session


def send_result(api_url: str, result: Dict[str, Any]):
    logging.error(result)
    response = make_session().post(f'http://{api_url}/internal/api/create_sample', json=result)
    assert response.status_code == 201
    return response
