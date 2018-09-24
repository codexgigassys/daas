from django.db import models
import hashlib


class Statistics(models.Model):
    timeout = models.FloatField()
    elapsed_time = models.FloatField()
    exit_status = models.IntegerField()
    timed_out = models.BooleanField()
    output = models.CharField(max_length=65000)
    errors = models.CharField(max_length=65000)


class Sample(models.Model):
    class Meta:
        ordering = ['sha1']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    data = models.BinaryField()
    date = models.DateField(auto_now=True)
    zip_result = models.BinaryField(default=None, blank=True, null=True)
    command_output = models.CharField(default='', max_length=65000, blank=True, null=True)
    statistics = models.ForeignKey(Statistics, default=None, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.sha1


    def set_result(self, file_path, command_output):
        # creae a zip using file_path
        self.command_output = command_output











