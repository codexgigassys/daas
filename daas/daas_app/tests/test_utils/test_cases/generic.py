from django.test import TestCase as DjangoTestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import LiveServerTestCase, Client, RequestFactory
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase as DRFAPITestCase
from typing import Optional
import time

from ....utils.connections.django_server import DjangoServerConfiguration
from ....views import UploadView
from ....models import Sample


class WithLoggedInClientMixin:
    """ To do requests as logged in user. The class needs a 'client' class attribute for this mixin to work. """
    @classmethod
    def _log_in(cls) -> None:
        logged_in = cls.client.login(username=cls._get_or_create_user(password='secret').username,
                                     password='secret')
        assert logged_in

    @classmethod
    def _get_or_create_user(cls, password) -> User:
        if not User.objects.filter(username='daas').exists():
            User.objects.create_superuser(username='daas', email='daas@mail.com', password=password)
        return User.objects.get(username='daas')

    @classmethod
    def upload_file(cls, file_path: Optional[str] = None, file_url: Optional[str] = None,
                    file_name: Optional[str] = None, force_reprocess: bool = False,
                    zip_password: Optional[str] = None) -> HttpResponse:
        """ Method to not repeat code on tests to upload files using the API.
            You should either pass 'file' or both 'file_url' and 'file_name'."""
        cls._log_in()
        data = {'force_reprocess': force_reprocess}
        if zip_password:
            data['zip_password'] = zip_password
        if file_path:
            with open(file_path, 'rb') as file:
                data['file'] = file
                # we can not take the following line outside the if-else because here we need to send the request before the file descriptor is closed.
                response = cls.client.post('/api/upload/', data, follow=True)
        else:
            data.update({'file_url': file_url, 'file_name': file_name})
            response = cls.client.post('/api/upload/', data, follow=True)

        # Verify the status code. We can not use assert<Something> methods here because they are not class methods.
        assert response.status_code == 202
        return response

    def wait_sample_creation(self, expected_samples: int) -> None:
        """ This function waits until samples are created.
        If it takes too long, the test will fail at this function. """
        tries = 0
        while tries < expected_samples * 5 or Sample.objects.count() < expected_samples:
            tries += 1
            time.sleep(1)
        assert Sample.objects.count() == expected_samples,\
            f'Samples in the database ({Sample.objects.count()}) should be equal to expected samples ({expected_samples})'

    def setUp(self) -> None:
        self._log_in()


class NonTransactionalLiveServerTestCase(LiveServerTestCase, WithLoggedInClientMixin):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = DjangoServerConfiguration().ip
        cls.port = DjangoServerConfiguration().renewed_testing_port
        super().setUpClass()
        cls.client = Client()
        cls._run_test_count = 0
        cls.factory = RequestFactory()

    @property
    def _total_test_count(self) -> int:
        return len([x for x in dir(self) if x[:5] == "test_"])

    @property
    def _all_tests_run(self) -> bool:
        return self._run_test_count == self._total_test_count

    @classmethod
    def _increase_run_test_count(cls) -> None:
        cls._run_test_count += 1

    def _post_teardown(self) -> None:
        """ This makes the test non-transactional.
            Otherwise, the DB will be flushed after every test. """
        self._increase_run_test_count()
        if self._all_tests_run:
            super()._post_teardown()

    def upload_file_through_web_view(self, file_name, follow=False, zip_password: str = None) -> HttpResponse:
        data = {'zip_password': zip_password} if zip_password else {}
        request = self.factory.post('upload_file/', data=data, format='json', follow=follow)

        with File(open(file_name, 'rb')) as file:
            request.FILES['file'] = SimpleUploadedFile(file_name, file.read())
        request.user = self._get_or_create_user(password='secret')

        response = UploadView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        return response


class APITestCase(DRFAPITestCase, WithLoggedInClientMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()
