from django.test import TestCase as DjangoTestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import LiveServerTestCase, Client, RequestFactory
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase as DRFAPITestCase

from ....utils.connections.django_server import DjangoServerConfiguration
from ....views import upload_file_view


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
    def upload_file(cls, file_path, force_reprocess=False, zip_password: str = None) -> HttpResponse:
        with open(file_path, 'rb') as file:
            data = {'force_reprocess': force_reprocess, 'file': file}
            if zip_password:
                data['zip_password'] = zip_password
            response = cls.client.post('/api/upload/', data)
        # Verify the status code. We can not use assert<Something> methods here because they are not class methods.
        assert response.status_code == 202
        return response

    def setUp(self) -> None:
        self._log_in()


class NonTransactionalLiveServerTestCase(LiveServerTestCase, WithLoggedInClientMixin):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = DjangoServerConfiguration().ip
        cls.port = DjangoServerConfiguration().port
        super().setUpClass()
        cls.client = Client()
        cls._run_test_count = 0

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


class TestCase(DjangoTestCase, WithLoggedInClientMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()
        cls.factory = RequestFactory()

    def upload_file_through_web_view(self, file_name, follow=False, zip_password: str = None) -> HttpResponse:
        data = {'zip_password': zip_password} if zip_password else {}
        request = self.factory.post('upload_file/', data=data, format='json', follow=follow)

        with File(open(file_name, 'rb')) as file:
            request.FILES['file'] = SimpleUploadedFile(file_name, file.read())
        request.user = self._get_or_create_user(password='secret')

        response = upload_file_view(request)
        self.assertEqual(response.status_code, 302)
        return response


class APITestCase(DRFAPITestCase, WithLoggedInClientMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()
