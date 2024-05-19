from pathlib import Path

from rest_framework import serializers
from rest_framework.reverse import reverse

from propylon_document_manager.file_versions.models import FileVersion, Document, File
from propylon_document_manager.file_versions.utils import get_file_digest


class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"


class DocumentCreateSerializer(serializers.Serializer):
    upload_file = serializers.FileField(max_length=255)
    file_location = serializers.CharField(max_length=255)

    def validate(self, data):
        upload_file = data["upload_file"]
        file_name = data["file_location"].split("/")[-1]

        if file_name != upload_file.name:
            raise serializers.ValidationError(
                "file_location filename must be same as the upload file"
            )

        file_digest = get_file_digest(upload_file)
        data["digest"] = file_digest
        return data

    def validate_file_location(self, value):
        if value[0] == "/" or value[-1] == "/":
            raise serializers.ValidationError(
                "Leading and trailing forward slashes not permitted"
            )
        return value

    def create(self, validated_data):
        upload_file = validated_data["upload_file"]
        file_location = validated_data["file_location"]
        digest = validated_data["digest"]
        current_user = validated_data["user"]

        file_path = Path(digest) / upload_file.name

        file, is_file_created = File.objects.get_or_create(
            file_name=upload_file.name, digest=validated_data["digest"]
        )

        if is_file_created:
            file.uploaded_file.save(file_path.as_posix(), upload_file)

        document, is_document_created = Document.objects.get_or_create(
            file=file, user=current_user, file_location=file_location
        )

        return document


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ("file_url", "version", "created_at", "modified_at", "file_location")
        depth = 1

    def get_file_url(self, obj: Document) -> str:
        return reverse("documents:download-file", args=[obj.file_location])

    def get_version(self, obj: Document) -> str:
        return obj.file.digest
