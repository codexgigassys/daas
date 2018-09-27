from django.db import models

class Sample(models.Model):
    class Meta:
        ordering = ['-id']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=120, unique=True)
    data = models.BinaryField(default=0, blank=True, null=True)
    size = models.IntegerField()
    date = models.DateField(auto_now=True)
    command_output = models.CharField(default='', max_length=65000, blank=True, null=True)

    def __str__(self):
        return self.name


class Statistics(models.Model):
    timeout = models.IntegerField(default=None, blank=True, null=True)
    elapsed_time = models.IntegerField(default=None, blank=True, null=True)
    exit_status = models.IntegerField(default=None, blank=True, null=True)
    timed_out = models.BooleanField(default=False)
    output = models.CharField(max_length=65000)
    errors = models.CharField(max_length=65000)
    zip_result = models.BinaryField(default=None, blank=True, null=True)
    decompiled = models.BooleanField(default=False)
    decompiler = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
