import socket
from django.conf import settings
import sys


class DjangoServerConfiguration:
    @property
    def ip(self):
        return socket.gethostbyname(socket.gethostname())

    @property
    def port(self):
        return settings.TEST_INSTANCE_PORT if ('test' in sys.argv) else settings.DEFAULT_PORT

    @property
    def base_url(self):
        return f'{self.ip}:{self.port}'
