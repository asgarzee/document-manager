from rest_framework import serializers

from propylon_document_manager.file_versions.models import FileVersion, Document, File


class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"


class DocumentCreateSerializer(serializers.Serializer):
    upload_file = serializers.FileField(max_length=255)
    file_path = serializers.CharField(max_length=255)

    def create(self, validated_data):
        upload_file = validated_data["upload_file"]
        file_path = validated_data["file_path"]
        file = File.objects.create(file_name=file_path)
        file.uploaded_file.save(file_path, upload_file)

        return Document.objects.create(file=file, user=validated_data["user"])
