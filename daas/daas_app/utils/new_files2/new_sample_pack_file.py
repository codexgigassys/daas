import logging

from .abstract_new_file import AbstractNewFile


class NewSamplePackFile(AbstractNewFile):
    def __init__(self, file_name: str, content: bytes, identifier: str = 'zip',
                 force_reprocess: bool = False, zip_password: bytes = b'') -> None:
        super().__init__(file_name, content, identifier, force_reprocess, zip_password)
        self.sub_files = []

    @property
    def already_exists(self) -> bool:
        return all(file.already_exists for file in self.sub_files)

    @property
    def will_be_processed(self) -> bool:
        return any(file.will_be_processed for file in self.sub_files)

    def upload(self) -> None:
        logging.info('Processing zip file.')
        zip_file = get_in_memory_zip_of(self.content)
        for file_name in zip_file.namelist():
            content = zip_file.read(file_name, pwd=self.zip_password)
            self._upload_sub_file(file_name, content)

    def _upload_sub_file(self, file_name: str, content: bytes) -> None:
        from .utils import create_and_upload_file  # Dynamic import to not fall into cyclic imports
        sub_file = create_and_upload_file(file_name, content, self.force_reprocess, self.zip_password)
        if sub_file:
            self.sub_files.append(sub_file)
