import logging
import hashlib
from functools import cached_property
from django.db import transaction

from .utils.file_utils import get_in_memory_zip_of
from .models import Sample, RedisJob
from .utils import classifier, zip_distributor
from .utils.redis_manager import RedisManager


class UploadedFile:
    def __init__(self, file_name: str, content: bytes, identifier: str, force_reprocess: bool = False,
                 zip_password: bytes = b''):
        self.content = content
        self.file_name = file_name
        self.force_reprocess = force_reprocess
        self.zip_password = zip_password
        self.identifier = identifier

    @cached_property
    def sha1(self) -> str:
        return hashlib.sha1(self.content).hexdigest()

    def requires_processing(self, sample: Sample) -> bool:
        return self.force_reprocess or sample.requires_processing


class Zip(UploadedFile):
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
        sub_file = create_uploaded_file_instance(file_name, content,
                                                 self.force_reprocess,
                                                 self.zip_password)
        self.sub_files.append(sub_file)
        sub_file.upload()


class NewSample(UploadedFile):
    def __init__(self, file_name: str, content: bytes, identifier: str = 'zip',
                 force_reprocess: bool = False, zip_password: bytes = b'') -> None:
        super().__init__(file_name, content, identifier, force_reprocess, zip_password)
        self.already_exists = False
        self.will_be_processed = False

    def upload(self) -> None:
        logging.info(f'Processing non-zip {self.identifier} file.')
        with transaction.atomic():
            self.already_exists, sample = Sample.objects.get_or_create(self.sha1, self.file_name, self.content, self.identifier)
            self.will_be_processed = self.requires_processing(sample)
            if self.will_be_processed:
                self._process_sample(sample)
                logging.info(f'File {self.sha1=} sent to the queue with {job_id=}')
            else:
                logging.info(f'File {self.sha1=} is not going to be processed again, because it\'s not needed and it\'s not foced.')

    def _process_sample(self, sample: Sample) -> None:
        _, job_id = RedisManager().submit_sample(sample)
        sample.wipe()  # for reprocessing or non-finished processing.
        RedisJob.objects.create(job_id=job_id, sample=sample)  # assign the new job to the sample


def create_uploaded_file_instance(file_name: str, content: bytes, force_reprocess: bool = False,
                                  zip_password: bytes = b'') -> UploadedFile:
    try:
        identifier = classifier.get_identifier_of_file(content)
    except classifier.ClassifierError:
        logging.info(f'There is no valid processor for file: {file_name}.')
    else:
        uploaded_file_class = Zip if identifier == 'zip' else NewSample
        return uploaded_file_class(file_name, content, identifier, force_reprocess, zip_password)
