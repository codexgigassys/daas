from django.db import models
import hashlib


class Sample(models.Model):
    class Meta:
        ordering = ['sha1']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    data = models.BinaryField()
    zip_result = models.BinaryField(default=None)
    command_output = models.CharField(default=None)
    statististics = '' # check model for dict

    def __str__(self):
        return self.sha1

    def __init__(self, content):
        self.data = content
        self.md5 = hashlib.md5(content).hexdigest()
        self.sha1 = hashlib.sha1(content).hexdigest()
        self.sha2 = hashlib.sha2(content).hexdigest()

    def set_result(self, file_path, command_output):
        # creae a zip using file_path
        self.command_output = command_output











