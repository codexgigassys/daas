import hashlib
import logging

from .seaweed import seaweedfs
from .classifier.classify import get_identifier_of_file
from .classifier.file_utils import get_in_memory_zip_of


class Sample:
    def __init__(self, file_name: str, content: bytes, password: bytes,
                 uploaded_on: str, seaweedfs_file_id: str = None) -> None:
        self.file_name = file_name
        self.content = content
        self.password = password
        self.seaweedfs_file_id = seaweedfs_file_id
        self.uploaded_on = uploaded_on
        self.file_type = get_identifier_of_file(self.content)
        self.subfiles = []
        if self.file_type == 'zip':
            self._load_subfiles()

    def _load_subfiles(self) -> None:
        logging.info('Processing zip file.')
        zip_file = get_in_memory_zip_of(self.content)
        for file_name in zip_file.namelist():
            content = zip_file.read(file_name, pwd=self.password)
            sample = Sample(file_name=file_name, content=content, password=b'', uploaded_on=self.uploaded_on)
            if sample.is_valid:
                self.subfiles.append(sample)
        self.delete_from_seaweedfs()  # delete the zip file
        self.seaweedfs_file_id = None

    @property
    def is_valid(self) -> bool:
        return self.content != b'' and self.file_type

    @property
    def size(self) -> int:
        return len(self.content)

    @property
    def md5(self) -> str:
        return hashlib.md5(self.content).hexdigest()

    @property
    def sha1(self) -> str:
        return hashlib.sha1(self.content).hexdigest()

    @property
    def sha2(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    @property
    def metadata(self) -> dict:
        return {'size': self.size,
                'md5': self.md5,
                'sha1': self.sha1,
                'sha2': self.sha2,
                'file_type': self.file_type,
                'seaweedfs_file_id': self.seaweedfs_file_id,
                'uploaded_on': self.uploaded_on,
                'file_name': self.file_name,
                'subfiles': [subfile.metadata for subfile in self.subfiles]}

    def delete_from_seaweedfs(self) -> None:
        if self.seaweedfs_file_id:
            seaweedfs.delete_file(self.seaweedfs_file_id)
