from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from ..views import upload_file


CSHARP = '/daas/daas/daas_app/tests/resources/460f0c273d1dc133ed7ac1e24049ac30.csharp'
TEXT = '/daas/daas/daas_app/tests/resources/text.txt'
FLASH = '/daas/daas/daas_app/tests/resources/995bb44df3d6b31d9422ddb9f3f78b7b.flash'
FLASH2 = '/daas/daas/daas_app/tests/resources/eb19009c086845d0408c52d495187380c5762b8c.flash'


class CustomTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.factory = RequestFactory()
        self.user = self.__get_or_create_user()
        super().__init__(*args, **kwargs)

    def __get_or_create_user(self):
        if User.objects.filter(username='daas').count() > 0:
            user = User.objects.get(username='daas')
        else:
            user = User.objects.create_user(username='daas', email='daas@mail.com', password='top_secret')
        return user

    def upload_file(self, file_name, follow=False):
        with File(open(file_name, 'rb')) as file:
            uploaded_file = SimpleUploadedFile(file_name, file.read(),
                                               content_type='multipart/form-data')
            request = self.factory.post('upload_file/', follow=follow)
            request.FILES['file'] = uploaded_file
        request.user = self.user
        return upload_file(request)


class PieChartCustomTestCase(CustomTestCase):
    fixtures = ['charts.json']
    chart = None  # set it on setUpClass method

    def get_samples_of(self, sample_type):
        return [series['value'] for series in self.chart['series'][0]['data'] if series['name'] == sample_type].pop()


class StackedBarChartCustomTestCase(CustomTestCase):
    fixtures = ['charts.json']
    chart = None  # set it on setUpClass method

    def get_series(self, name):
        return [series['data'] for series in self.chart['series'] if series['name'] == name].pop()

    def get_element_count_of_single_series(self, name):
        return sum(self.get_series(name))

    def get_element_count_of_multiple_series(self, names):
        return sum([self.get_element_count_of_single_series(name) for name in names])


class DataZoomChartCustomTestCase(StackedBarChartCustomTestCase):
    def assertListEqual(self, actual, expected):
        number_of_expected_items = len(expected)
        number_of_unexpected_items = len(actual) - number_of_expected_items
        super().assertListEqual(actual[:number_of_expected_items], expected)
        # from the latest day to today, the data zoom chart will generate a date with zero items
        super().assertListEqual(actual[number_of_expected_items:], [0] * number_of_unexpected_items)

    def assertDateListEqual(self, actual, expected):
        length = len(expected)
        super().assertListEqual(actual[:length], expected)


def generate_worker_result(sample, timeout=120, elapsed_time=5, failed=False, decompiler_name='mock decompiler'):
    timed_out = elapsed_time >= timeout
    exit_status = 124 if timed_out else (1 if failed else 0)
    info_for_statistics = {'sha1': sample.sha1,
                           'timeout': timeout,
                           'elapsed_time': elapsed_time + 1,
                           'exit_status': exit_status,
                           'timed_out': timed_out,
                           'output': 'decompiler output',
                           'decompiled': exit_status == 0,
                           'decompiler': decompiler_name,
                           'version': 1}
    return {'statistics': info_for_statistics, 'zip': 'fake zip'}
