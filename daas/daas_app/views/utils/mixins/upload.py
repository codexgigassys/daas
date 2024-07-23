from typing import Optional, TextIO
from pyseaweed import WeedFS
from django.conf import settings

from ....utils.task_manager import TaskManager


class UploadMixin:
    def upload(self, file: Optional[TextIO] = None, external_url: Optional[str] = None,
               file_name: Optional[str] = None, zip_password: str = '', force_reprocess: bool = False,
               callback: Optional[str] = None) -> bool:
        """ Either file or external_url should be specified. Other parameters are optional.
            Returns whether the upload was successful or not.
            Use this method to upload files to the metadata extractor."""
        successful_upload = True

        if file or external_url:
            file_name = self._get_file_name(file, file_name)
            upload_parameters = {'zip_password': zip_password,
                                 'force_reprocess': force_reprocess,
                                 'callback': callback,
                                 'file_name': file_name}
            if file:
                # Upload the file and send the file ID on seaweedfs
                seaweedfs = WeedFS(settings.SEAWEEDFS_IP,
                                   settings.SEAWEEDFS_PORT)
                upload_parameters['seaweedfs_file_id'] = seaweedfs.upload_file(stream=file.read(),
                                                                               name=file_name)
            else:
                # Send the url to download the file on the metadata extractor to avoid an overflow of the API if
                # lots of files are sent at the same time
                upload_parameters['external_url'] = external_url
            TaskManager().submit_url_for_metadata_extractor(**upload_parameters)
        else:
            successful_upload = False
        return successful_upload

    def _get_file_name(self, file: Optional[TextIO] = None,  file_name: Optional[str] = None) -> str:
        if not file_name:
            file_name = file.name if file else 'Unnamed file'
        return file_name
