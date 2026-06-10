import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_RETRY = Retry(connect=5, backoff_factor=1, raise_on_status=False)
_ADAPTER = HTTPAdapter(max_retries=_RETRY)


def make_session() -> requests.Session:
    session = requests.Session()
    session.mount('http://', _ADAPTER)
    return session
