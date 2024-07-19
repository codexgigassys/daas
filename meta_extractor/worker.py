import logging
import os
from typing import Dict, Any

from . import api_connector
from .redis.task import Task


# This function should by called by redis queue (rq command).
def worker(task_settings: Dict[str, Any]) -> None:
    if os.environ.get('CIRCLECI'):
        logging.getLogger().setLevel(logging.DEBUG)
    # Instantiate the task and process the sample
    task = Task(task_settings=task_settings)

    # Set up the response
    response = {'force_reprocess': task.force_reprocess,
                'callback': task.callback}
    if task.sample_found:
        if not task.sample.is_zip:  # Real samples
            response['sample'] = task.sample.metadata
        else:  # Zip files with samples or even more zip files inside
            task.split_into_subtasks_per_subfile()

    # Send the response
    api_connector.send_result(task.api_url, response)
    logging.info(f'Response sent to api for {task.sample.sha1=}')
