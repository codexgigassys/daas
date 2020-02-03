from ...test_utils.test_cases.generic import APITestCase
from ....models import Sample


class GetSamplesFromHashTest(APITestCase):
    def setUp(self) -> None:
        self.sample = Sample.objects.create(size=155, md5='a'*32, sha1='b'*40, sha2='c'*64, file_type='flash',
                                            seaweedfs_file_id='3,01637037d6', uploaded_on='2020-01-15',
                                            file_name='flash_sample.swf')

    def test_no_samples(self):
        self.sample.delete()
        response = self.client.get(f'/api/get_sample_from_hash/{"0"*40}', format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_one_sample_using_md5(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.md5}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('md5'), self.sample.md5)

    def test_get_one_sample_using_sha1(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.sha1}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha1'), self.sample.sha1)

    def test_get_one_sample_using_sha2(self):
        response = self.client.get(f'/api/get_sample_from_hash/{self.sample.sha2}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('sha2'), self.sample.sha2)
