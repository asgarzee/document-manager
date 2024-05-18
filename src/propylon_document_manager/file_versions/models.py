from django.db import models

from propylon_document_manager.accounts.models import User


class FileBase(models.Model):
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class File(FileBase):
    file_name = models.CharField(max_length=255)
    uploaded_file = models.FileField()
    digest = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.file_name


class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField()


class Document(FileBase):
    file = models.ForeignKey(File, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    file_location = models.CharField(max_length=255, unique=True)
