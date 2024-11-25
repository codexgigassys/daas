import hashlib
import time
from .test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from .test_utils.resource_directories import CSHARP_SAMPLE, FLASH_SAMPLE_01, FLASH_SAMPLE_02, TEXT_SAMPLE
from ..models import Sample


class TestDownloadView(NonTransactionalLiveServerTestCase):
    def test_download(self):
        r = self.upload_file(TEXT_SAMPLE)
        assert r.status_code == 202, "r.status_code was %s" % r.status_code
        time.sleep(9)
        sample = Sample.objects.first()
        assert sample is not None
        self.download_file(sample)
    
    @classmethod
    def download_file(cls, sample):
        sha1 = hashlib.sha1(open(TEXT_SAMPLE, 'rb').read()).digest()
        cls._log_in()
        response = cls.client.get('/internal/api/download_sample/%s' % sample.id, follow=True)
        assert response.status_code == 200, f'status code should be 200, but it is {response.status_code}'

        return response
