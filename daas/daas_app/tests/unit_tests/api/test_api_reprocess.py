from ...test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ....models import Sample, Result
from ....utils.callback_manager import CallbackManager


class ReprocessAPITest(NonTransactionalLiveServerTestCase):
    def setUp(self):
        self.sample = Sample.objects.create(size=155, md5='a'*32, sha1='b'*40, sha2='c'*64, file_type='flash',
                                            seaweedfs_file_id='3,01637037d6', uploaded_on='2020-01-15',
                                            file_name='flash_sample.swf')
        Result.objects.create(status=1, output='', decompiler='decompiler', sample=self.sample,
                              extension='exe', version=0, seaweed_result_id='')
        CallbackManager().__mock__()  # to avoid serializing non-existent results due to the mocking of TaskManager

    def tearDown(self) -> None:
        """ We need to wipe the db because the test case superclass is non-transactional """
        Sample.objects.all().delete()
        Result.objects.all().delete()

    def test_reprocess_with_md5(self):
        response = self.reprocess([self.sample.md5])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_reprocess_with_sha1(self):
        response = self.reprocess([self.sample.sha1])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_reprocess_with_sha2(self):
        response = self.reprocess([self.sample.sha2])
        self.assertEqual(response.json()['submitted_samples'], 1)

    def test_force_reprocess(self):
        response = self.reprocess([self.sample.md5], True)
        self.assertEqual(response.json()['submitted_samples'], 1)
