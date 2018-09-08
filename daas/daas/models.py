from django.db import models


class Sample(models.Model):
    class Meta:
        ordering = ['sha1']
    md5 = models.CharField(max_length=100, unique=True)
    sha1 = models.CharField(max_length=100, unique=True)
    sha2 = models.CharField(max_length=100, unique=True)
    data = models.BinaryField()
    zip_result = models.BinaryField(default=None)
    command_output = models.CharField(default=None)

    def __str__(self):
        return self.sha1
