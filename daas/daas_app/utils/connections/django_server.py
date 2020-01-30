from ..singleton import ThreadSafeSingleton

import socket
from django.conf import settings
import sys


class DjangoServerConfiguration(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.testing_port = settings.TEST_INSTANCE_PORT

    @property
    def ip(self):
        return socket.gethostbyname(socket.gethostname())

    @property
    def renewed_testing_port(self) -> int:
        """ Return a new port to not try to used an already used port. """
        while not self._testing_port_is_available():
            self.testing_port += 1
        self.testing_port += 1  # to not use the same port again
        testing_port = self.testing_port
        return testing_port

    def _testing_port_is_available(self):
        """ Returns whether a port is available or not. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("0.0.0.0", self.testing_port))
            except:
                available = False
            else:
                available = True
        return available

    @property
    def port(self):
        """ Returns the default port. If running tests, returns the first available port starting from the
            default test port defined on settings.py. """
        return self.testing_port if ('test' in sys.argv) else settings.DEFAULT_PORT

    @property
    def base_url(self):
        return f'{self.ip}:{self.port}'
