from typing import List, Tuple, Union
from django.db import models


class SampleAdapter:
    """ Adapter to easily get information from a sample in the expected format. """
    def __init__(self, sample: models.Model):
        self._sample = sample

    @property
    def file_type(self):
        return self._sample.file_type

    def get_fields_and_values(self, fields: List[str]) -> List[Tuple[str, Union[str, int]]]:
        return [self._get_field_and_value(field) for field in fields]

    def _get_field_and_value(self, field: str) -> Tuple[str, Union[str, int]]:
        if not hasattr(self, f'_{field}'):
            raise AttributeError(f'Field {field} not adapted.')
        return field, eval(f'self._{field}')

    @property
    def _uploaded_on(self) -> Tuple[str, str]:
        return 'uploaded_on', self._sample.uploaded_on.date().isoformat()

    @property
    def _size(self) -> Tuple[str, str]:
        """ returns size in kb """
        return 'size', str(int(self._sample.size/1024))

    @property
    def _status(self) -> Tuple[str, str]:
        return 'status', str(self._sample.result.status)

    @property
    def _processed_on(self) -> Tuple[str, str]:
        return 'processed_on', self._sample.result.processed_on.date().isoformat()

    @property
    def _elapsed_time(self) -> Tuple[str, str]:
        """ returns elapsed time in seconds. """
        return 'elapsed_time', str(self._sample.result.elapsed_time)
