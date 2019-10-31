import hashlib
from functools import cached_property

from ...models import Sample


class AbstractNewFile:
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

    def upload(self) -> None:
        raise NotImplementedError()
