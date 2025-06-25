import logging
import os
from typing import Dict, Any
from str_to_bool import str_to_bool

from .decompiler_factory import DecompilerFactory
from .utils import send_result, get_sample, save_result


# This function should by called by redis queue (rq command).
def worker(task: Dict[str, Any]) -> None:
    if str_to_bool(os.environ.get('CIRCLECI')) or not str_to_bool(os.environ.get('DJANGO_PRODUCTION')):
        logging.getLogger().setLevel(logging.DEBUG)
    decompiler = DecompilerFactory().create(task['config'])
    sample = get_sample(task['seaweedfs_file_id'])
    if sample is None:
        logging.error('Sample not found on seaweedfs: %s' % task['seaweedfs_file_id'])
    else:
        result = decompiler.process(sample)
        save_result(result)
        send_result(result, task['api_base_url'])
