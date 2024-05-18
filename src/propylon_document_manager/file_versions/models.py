from django.db import models


class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField()
