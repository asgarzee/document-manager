from django.db import models

from propylon_document_manager.accounts.models import User


class File(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_file = models.FileField()

    def __str__(self):
        return self.file_name


class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField()


class Document(models.Model):
    file = models.OneToOneField(File, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
