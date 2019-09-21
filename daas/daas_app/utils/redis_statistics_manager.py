from django_redis import get_redis_connection
import datetime
from typing import SupportsBytes


class RedisStatistcsManager:
    def __init__(self):
        self.redis = get_redis_connection("default")
        self.fields = ['result.status', 'size', 'uploaded_on', 'result.processed_on']
    # fixme: cuando se reprocesa no hay que contar el size y eso de nuevo, pero puede ser que varie
    """ el tiempo que tarda, el status que devuelve, etc. Respecto al processed on, creo que deberiamos dejar
        ambas fechas, para no perder tracking de cuanto procesamos cada dia. Sino contar"""

    def _date(self, year, month, day):
        return datetime.date(year, month, day).isoformat()

    def register_sample(self, sample):
        fields_and_values = [self._get_uploaded_on(sample),
                             self._get_processed_on(sample),
                             self._get_size(sample),
                             self._get_status(sample),
                             self._get_elapsed_time(sample)]
        for field, value in fields_and_values:
            self._register_field_and_value(sample.file_type, field, value)

    def _register_field_and_value(self, file_type: SupportsBytes, field: SupportsBytes, value: SupportsBytes):
        """ For instance, register_at_field(file_type="flash", field="seconds", value="12")
            register that a flash sample needed 12 seconds to be decompiled"""
        self.redis.hincrby(f'{file_type}.{field}', value, 1)

    def _get_uploaded_on(self, sample):
        return 'uploaded_on', sample.uploaded_on.date.isoformat()

    def _get_processed_on(self, sample):
        return 'processed_on', sample.result.processed_on.date.isoformat()

    def _get_size(self, sample):
        return 'size', sample.size

    def _get_status(self, sample):
        return 'status', sample.result.status

    def _get_elapsed_time(self, sample):
        return 'elapsed_time', sample.result.elapsed_time
