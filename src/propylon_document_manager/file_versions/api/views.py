from http import HTTPMethod
from typing import Any

from rest_framework import status
from django.http import FileResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

from .serializers import FileVersionSerializer, DocumentCreateSerializer, DocumentSerializer
from ..models import FileVersion, Document


class DocumentViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]

    def upload_file(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({}, status=status.HTTP_201_CREATED)

    def get_object(self, version: str):
        return Document.objects.get(file__digest=version, user=self.request.user)

    def get_file_version(self, request: Request, version: str, *args, **kwargs) -> Response:
        try:
            instance = self.get_object(version)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(instance)
        return Response(serializer.data)

    def download_file(self, request, file_path):
        try:
            document = Document.objects.get(file_location=file_path, user=self.request.user)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(document.file.uploaded_file, as_attachment=True)

