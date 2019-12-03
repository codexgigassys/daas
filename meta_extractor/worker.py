from .get_sample import get_sample
from .process import process
from .send_generic_reuslt import send_generic_reuslt


# This function should by called by redis queue (rq command).
def worker(task):
    download_url = task['download_url']
    callback = task['callback']
    api_url = task['api_url']
    sample = get_sample(download_url)
    metadata = {'sample_found': False,
                'callback': callback}
    if sample:
        metadata.update(process(sample))
        metadata['sample_found'] = True
    send_generic_reuslt(api_url, metadata)
