import subprocess
from django.test import TestCase


class TestPEP8(TestCase):
    def test_pep8(self):
        output = subprocess.check_output(
            ["find", "/daas/", "-type", "f", "-name",
             "*.py", "-exec", "pycodestyle", "--max-line-length=34000",
             "--ignore=E121,E123,E126,E203,E226,E231,E24,E704,W503,W605,E741,E701,E722",
             "{}", ";"])
        assert len(output.strip()) == 0, 'Should be zero. (PEP8 test failed)\n' + str(output.strip())
