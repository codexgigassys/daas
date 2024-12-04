import hashlib
from ...test_utils.test_cases.generic import NonTransactionalLiveServerTestCase


class TestStatisticsView(NonTransactionalLiveServerTestCase):
    def test_statistics(self):
        for url in ['/statistics/samples_per_size_data/',
                    '/statistics/samples_per_size/',
                    '/statistics/samples_per_elapsed_time/',
                    '/statistics/samples_per_elapsed_time_data/',
                    '/statistics/samples_per_type/',
                    '/statistics/samples_per_type_data/',
                    '/statistics/samples_per_upload_date/',
                    '/statistics/samples_per_upload_date_data/',
                    '/statistics/samples_per_process_date/',
                    '/statistics/samples_per_process_date_data/',
                    '/statistics/samples_per_status/apk/',
                    '/statistics/samples_per_status_data/apk/']:
            r = self.custom_get(url)
            assert r.status_code == 200, "r.status_code was %s" % r.status_code
            if url[-5:] == '_data':
                assert isinstance(r.json(), dict)
