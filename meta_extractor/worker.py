import logging

from . import api_connector
from .redis.task import Task


# This function should by called by redis queue (rq command).
def worker(task_settings):
    # Instantiate the task and process the sample
    task = Task(task_settings=task_settings)

    # Set up the response
    response = {'force_reprocess': task.force_reprocess,
                'callback': task.callback}
    if task.sample_found:
        response['sample'] = task.sample.metadata

    # Send the response
    api_connector.send_result(task.api_url, response)
    logging.info(f'Response sent to api for {task.sample.sha1=}')
