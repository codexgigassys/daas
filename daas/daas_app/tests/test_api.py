from .test_utils import CustomAPITestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, FLASH2


class GetSamplesFromHashTest(CustomAPITestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_no_samples(self):
        data = {'sha1': ['5hvt44tgtg4g', '0'*40, 'adsadsadsdasdsad']}
        response = self.post('/api/get_samples_from_hashes/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_get_one_sample_using_sha1(self):
        self.upload_file(CSHARP)
        sha1 = Sample.objects.all()[0].sha1
        md5 = Sample.objects.all()[0].md5
        data = {'sha1': ['5hvt44tgtg4g', sha1, 'adsadsadsdasdsad']}
        response = self.post('/api/get_samples_from_hashes/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("md5"), md5)

    def test_get_two_samples_using_md5_and_sha2(self):
        self.upload_file(CSHARP)
        self.upload_file(FLASH)
        sha2 = Sample.objects.all()[0].sha2
        md5 = Sample.objects.all()[1].md5
        data = {'md5': ['4gvy5d4', md5, 'asda'],
                'sha2': ['5hvt44tgtg4g', sha2, 'adsadsadsdasdsad']}
        response = self.post('/api/get_samples_from_hashes/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("sha2"), sha2)
        self.assertEqual(response.data[1].get("md5"), md5)


class GetSamplesFromFileType(CustomAPITestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_no_samples_for_pe(self):
        response = self.get('/api/get_samples_from_file_type?file_type=pe')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_get_one_sample_for_pe(self):
        self.upload_file(CSHARP)
        file_type = Sample.objects.all()[0].file_type
        response = self.get('/api/get_samples_from_file_type?file_type=%s' % file_type)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("file_type"), file_type)

    def test_get_two_samples_for_flash(self):
        self.upload_file(FLASH)
        self.upload_file(FLASH2)
        file_type = Sample.objects.all()[0].file_type
        response = self.get('/api/get_samples_from_file_type?file_type=%s' % file_type)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("file_type"), file_type)
        self.assertEqual(response.data[1].get("file_type"), file_type)

    def test_not_samples_for_other_file_types(self):
        self.upload_file(FLASH)
        self.upload_file(FLASH2)
        Sample.objects.all()[0].file_type
        response = self.get('/api/get_samples_from_file_type?file_type=pe')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_not_samples_for_other_file_types(self):
        self.upload_file(FLASH)
        self.upload_file(CSHARP)
        flash = Sample.objects.all()[0].file_type
        pe = Sample.objects.all()[0].file_type
        response = self.get('/api/get_samples_from_file_type?file_type=%s,%s' % (flash, pe))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("file_type"), flash)
        self.assertEqual(response.data[1].get("file_type"), pe)
