from typing import Dict, Any

from .decompiler_factory import DecompilerFactory
from .utils import send_result, get_sample, save_result


# This function should by called by redis queue (rq command).
def worker(task: Dict[str, Any]) -> None:
    decompiler = DecompilerFactory().create(task['config'])
    sample = get_sample(task['seaweedfs_file_id'])
    result = decompiler.process(sample)
    save_result(result)
    send_result(result, task['api_base_url'])
