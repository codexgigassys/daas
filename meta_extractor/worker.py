from .send_metadata import send_metadata
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
    send_metadata(task.api_url, response)
