from django.db import transaction, IntegrityError
from django.urls import reverse
from django.test import RequestFactory
from rest_framework.views import APIView
from django.test import TestCase
import json

from .test_utils import CustomAPITestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, TEXT, ZIP


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
