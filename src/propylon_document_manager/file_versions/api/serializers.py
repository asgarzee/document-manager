from pathlib import Path

from rest_framework import serializers

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

        try:
            document = Document.objects.get(file=file, user=current_user)
        except Document.DoesNotExist:
            document = Document.objects.create(
                file=file, user=current_user, file_location=file_location
            )

        return document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        exclude = ["user"]
        depth = 1
