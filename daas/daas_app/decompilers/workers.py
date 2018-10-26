import requests
from .decompiler_config import csharp, flash
from .decompiler_factory import DecompilerCreator


# This function should by called by redis queue (rq command).
def redis_worker(task, config):
    send_result(DecompilerCreator().create(config).process(task['sample']))


def pe_worker(task):
    redis_worker(task, csharp)
    return


def flash_worker(task):
    redis_worker(task, flash)
    return


def send_result(result):
    url = "http://api:8000/set_result"
    payload = {'result': str(result)}
    response = requests.post(url, payload)
    return response

# we can replace the second argument by task['file_type'] and save it before sending the task
