from typing import Optional, Tuple
import requests
import time
import logging

from ..gridfs import storage
# from .requeue import TaskRequeuer
from .queue import TaskQueue
from ..sample import Sample
from .. import api_connector


class Task:
    def __init__(self, task_settings: dict) -> None:

        # Retrieve task paramters from tasks sent by redis queue
        self.settings = task_settings
        self.force_reprocess = task_settings['force_reprocess']
        self.callback = task_settings.get('callback')
        self.storage_file_id = task_settings.get('storage_file_id')
        self.external_url = task_settings.get('external_url')
        self.api_url = task_settings['api_url']
        file_name = task_settings.get('file_name')
        content, storage_file_id = self._get_sample_content(file_name)
        if content:
            self.sample = Sample(file_name=file_name,
                                 content=content,
                                 password=bytes(task_settings.get('zip_password', '').encode('utf-8')),
                                 storage_file_id=storage_file_id,
                                 uploaded_on=task_settings.get('uploaded_on'))

    def _get_sample_content(self, file_name: str) -> Tuple[Optional[bytes], str]:
        if self.storage_file_id:
            content = storage.get_file(self.storage_file_id)
        elif self.external_url:
            if content := self._get_sample_content_from_external_url(self.external_url):  # Sample downloaded
                self.storage_file_id = storage.upload_file(stream=content, name=file_name)
            else:  # Sample not accessible at the moment through the given URL
                # TaskRequeuer().requeue(self.settings)
                TaskQueue().requeue(self.settings)
                raise Exception('Sample not downloadable. Task requeued with low priority.')
        else:
            logging.error('Tasks should have one the following parameters: storage_file_id or external_url.\n' +
                          f'The current task has neither of them.')
            raise Exception('Missing required parameters: storage_file_id or external_url. At least one should be present.')
        return content, self.storage_file_id

    def _get_sample_content_from_external_url(self, download_url: str) -> Optional[bytes]:
        retries = 0
        response = requests.get(download_url)
        while response.status_code != 200 and retries < 10:
            retries += 1
            response = requests.get(download_url)
            time.sleep(max(1, (retries - 3) ** 2))
        return response.content if retries < 10 else None

    @property
    def sample_found(self) -> bool:
        return self.sample is not None

    def split_into_subtasks_per_subfile(self) -> None:
        for subfile in self.sample.subfiles:
            subfile_storage_file_id = storage.upload_file(stream=subfile.content, name=subfile.file_name)
            TaskQueue().add_subfile_to_queue(self.settings, subfile_storage_file_id)
