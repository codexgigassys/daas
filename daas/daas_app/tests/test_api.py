from django.db import transaction, IntegrityError
from django.urls import reverse
from django.test import RequestFactory
from rest_framework.views import APIView
from django.test import TestCase
import json

from .test_utils import CustomTestCase
from ..models import Sample
from ..utils.redis_manager import RedisManager
from .test_utils import CSHARP, FLASH, TEXT, ZIP
from ..api import GetSamplesFromHash, GetSamplesFromFileType, GetSamplesWithSizeBetween


class GetSamplesFromHashTest(TestCase):
    def setUp(self):
        RedisManager().__mock__()

    def test_get_samples_from_hash(self):
        response = CustomTestCase().upload_file(CSHARP)
        self.assertEqual(response.status_code, 302)
        sha1 = Sample.objects.all()[0].sha1
        md5 = Sample.objects.all()[0].md5
        data = {'sha1': ['5hvt44tgtg4g', sha1, 'adsadsadsdasdsad']}
        response = self.client.post('/api/get_samples_from_hashes/',
                                    json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None
        self.assertEqual(response.data[0].get("md5"), md5)
