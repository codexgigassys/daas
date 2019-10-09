import socket
from django.conf import settings
import sys


class DjangoServerConfiguration:
    @property
    def ip(self):
        return socket.gethostbyname(socket.gethostname())

    def _get_port_for_test_instance(self, increment: int = 0):
        port = settings.TEST_INSTANCE_PORT + increment
        return port if self._is_available(port) else self._get_port_for_test_instance(increment + 1)

    def _is_available(self, port):
        """ Returns whether a port is available or not. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("0.0.0.0", port))
            except:
                available = False
            else:
                available = True
        return available

    @property
    def port(self):
        """ Returns the default port. If running tests, returns the first available port starting from the
            default test port defined on settings.py. """
        return self._get_port_for_test_instance() if ('test' in sys.argv) else settings.DEFAULT_PORT

    @property
    def base_url(self):
        return f'{self.ip}:{self.port}'
