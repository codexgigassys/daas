import requests
from .decompiler_config import csharp, flash
from .decompiler_factory import DecompilerCreator


# This function should by called by redis queue (rq command).
def redis_worker(task, decompiler):
    worker = decompiler(task['sample'])
    send_result(worker.process())


def pe_redis_worker(task):
    send_result(DecompilerCreator().create(csharp).process(task['sample']))
    return


def flash_redis_worker(task):
    send_result(DecompilerCreator().create(flash).process(task['sample']))
    return


def send_result(result):
    url = "http://api:8000/set_result"
    payload = {'result': str(result)}
    response = requests.post(url, payload)
    return response
