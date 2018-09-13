from django.db import models
import hashlib


class Statistics(models.Model):
    timeout = models.FloatField()
    elapsed_time = models.FloatField()
    exit_status = models.IntegerField()
    timed_out = models.BooleanField()
    exception_info = models.CharField()
    output = models.CharField()
    errors = models.CharField()

    def __init__(self, timeout, elapsed_time, exit_status, timed_out, exception_info=None, output=None, errors=None):
        self.timeout = timeout
        self.elapsed_time = elapsed_time
        self.exit_status = exit_status
        self.timed_out = timed_out
        self.exception_info = exception_info
        self.output = output
        self.errors = errors


class Sample(models.Model):
    class Meta:
        ordering = ['sha1']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    data = models.BinaryField()
    zip_result = models.BinaryField(default=None)
    command_output = models.CharField(default=None)
    statistics = models.ForeignKey(Statistics, on_delete=models.CASCADE)

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











