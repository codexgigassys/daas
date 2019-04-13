from .test_utils import CustomAPITestCase
from ..models import Sample, Result
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, FLASH2
from ..utils.callback_manager import CallbackManager


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


class GetSamplesFromFileTypeTest(CustomAPITestCase):
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

    def test_no_samples_for_other_file_types(self):
        self.upload_file(FLASH)
        self.upload_file(FLASH2)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(Sample.objects.with_file_type_in(['pe']).count(), 0)
        response = self.get('/api/get_samples_from_file_type?file_type=pe')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_samples_for_multiple_file_types_found(self):
        self.upload_file(FLASH)
        self.upload_file(CSHARP)
        flash = Sample.objects.all()[0].file_type
        pe = Sample.objects.all()[1].file_type
        response = self.get('/api/get_samples_from_file_type?file_type=%s,%s' % (flash, pe))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("file_type"), flash)
        self.assertEqual(response.data[1].get("file_type"), pe)


class GetSamplesWithSizeBetweenTest(CustomAPITestCase):
    def test_no_samples_in_db(self):
        response = self.get('/api/get_samples_with_size_between?lower_size=%s&top_size=%s' % (0, 9999))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_no_samples_in_range(self):
        self.upload_file(FLASH)
        self.upload_file(CSHARP)
        response = self.get('/api/get_samples_with_size_between?lower_size=%s&top_size=%s' % (44, 55))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_one_sample_in_range(self):
        self.upload_file(FLASH)
        self.upload_file(CSHARP)
        response = self.get('/api/get_samples_with_size_between?lower_size=%s&top_size=%s' % (40*1000, 400*1000))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_two_samples_in_range(self):
        self.upload_file(FLASH)
        self.upload_file(CSHARP)
        response = self.get('/api/get_samples_with_size_between?lower_size=%s&top_size=%s' % (0, 9999))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class UploadAPITest(CustomAPITestCase):
    def test_upload_a_sample(self):
        self.upload_file_api(CSHARP)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(Sample.objects.all()[0].name, '460f0c273d1dc133ed7ac1e24049ac30.csharp')

    def test_upload_two_samples(self):
        self.upload_file_api(CSHARP)
        self.upload_file_api(FLASH)
        self.assertEqual(Sample.objects.count(), 2)

    def test_file_type_correctly_detected(self):
        self.upload_file_api(FLASH)
        self.assertEqual(Sample.objects.all()[0].file_type, 'flash')

    def test_file_content_not_modified(self):
        self.upload_file_api(FLASH2)
        self.assertEqual(Sample.objects.all()[0].sha1, 'eb19009c086845d0408c52d495187380c5762b8c')


class ReprocessAPITest(CustomAPITestCase):
    def setUp(self):
        RedisManager().__mock__()  # to avoid uploading samples for real
        self.upload_file(CSHARP)
        self.sample = Sample.objects.all()[0]
        RedisManager().__mock__()  # to reset submit sample calls to zero
        CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of RedisManager

    def test_nothing_to_reprocess(self):
        data = {'md5': [self.sample.md5]}
        self.post('/api/reprocess/', data)
        self.assertEqual(RedisManager().__mock_calls_submit_sample__(), 0)

    def test_reprocess(self):
        self.upload_file(CSHARP)
        Result.objects.update(version=-1)
        data = {'md5': [self.sample.md5]}
        self.post('/api/reprocess/', data)
        self.assertEqual(RedisManager().__mock_calls_submit_sample__(), 1)

    def test_force_reprocess(self):
        data = {'md5': [self.sample.md5], 'force_reprocess': True}
        self.post('/api/reprocess/', data)
        self.assertEqual(RedisManager().__mock_calls_submit_sample__(), 1)
