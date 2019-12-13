from pyseaweed import WeedFS
import logging

from .get_sample import get_sample
from .get_sample_metadata import get_sample_metadata
from .send_metadata import send_metadata
from .requeue import TaskRequeuer
from .zip_extractor import save_and_get_metadata_of_zip_subfiles


# This function should by called by redis queue (rq command).
def worker(task):
    # Get task parameters before processing the sample
    zip_password = bytes(task.get('zip_password', '').encode('utf-8'))
    force_reprocess = task['force_reprocess']
    callback = task.get('callback')
    seaweedfs_file_id = task.get('seaweedfs_file_id')
    external_url = task.get('external_url')
    file_name = task['file_name']
    uploaded_on = task['uploaded_on']
    api_url = task['api_url']

    # Get the sample and, if necessary, save it on Seaweed FS
    sample = None
    seaweedfs = WeedFS('seaweedfs_master', 9333)
    if seaweedfs_file_id:
        sample = seaweedfs.get_file(seaweedfs_file_id)
    elif external_url:
        sample = get_sample(external_url)
        if sample:  # Sample downloadable
            task['seaweedfs_file_id'] = seaweedfs.upload_file(stream=sample, name=file_name)
        else:  # Sample not accessible at the moment through the given URL
            TaskRequeuer().requeue(task)
    else:
        logging.error('Tasks should have one the following parameters completed: seaweedfs_file_id or external_url.\n' +
                      f'The current task has neither of them: {task=}.')

    # Process the sample
    response = {'sample_found': False,
                'force_reprocess': force_reprocess,
                'callback': callback,
                'seaweedfs_file_id': seaweedfs_file_id,
                'file_name': file_name,
                'uploaded_on': uploaded_on}

    if sample:
        metadata = get_sample_metadata(sample)
        response.update(metadata)
        if metadata['file_type'] == 'zip':
            metadata['subfiles_metadata'] = save_and_get_metadata_of_zip_subfiles(sample, zip_password, force_reprocess)
            seaweedfs.delete_file(seaweedfs_file_id)  # delete the zip file
        response['sample_found'] = True
    send_metadata(api_url, response)
