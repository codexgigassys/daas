import requests
import time
from typing import Optional


def get_sample(download_url: str) -> Optional[bytes]:
    retries = 0
    response = requests.get(download_url)
    while response.status_code != 200 and retries < 10:
        retries += 1
        response = requests.get(download_url)
        time.sleep(max(1, (retries - 3) ** 2))
    return response.content if retries < 10 else None
