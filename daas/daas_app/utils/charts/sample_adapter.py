from typing import List, Tuple
from django.db import models


class SampleAdapter:
    """ Adapter to easily get information from a sample in the expected format. """
    def __init__(self, sample: models.Model) -> None:
        self._sample = sample

    @property
    def file_type(self) -> str:
        return self._sample.file_type

    def get_fields_and_values(self, fields: List[str]) -> List[Tuple[str, str]]:
        return [self._get_field_and_value(field) for field in fields]

    def _get_field_and_value(self, field: str) -> Tuple[str, str]:
        if not hasattr(self, f'_{field}'):
            raise AttributeError(f'Field {field} not adapted.')
        return field, eval(f'self._{field}')

    @property
    def _uploaded_on(self) -> str:
        return self._sample.uploaded_on.date().isoformat()

    @property
    def _size(self) -> str:
        """ returns size in kb """
        return str(int(self._sample.size/1024))

    @property
    def _status(self) -> str:
        return str(self._sample.result.status)

    @property
    def _processed_on(self) -> str:
        return self._sample.result.processed_on.date().isoformat()

    @property
    def _elapsed_time(self) -> str:
        """ returns elapsed time in seconds. """
        return str(self._sample.result.elapsed_time)
