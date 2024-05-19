from typing import Any

from rest_framework import status
from django.http import FileResponse
from rest_framework.authentication import TokenAuthentication

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import DocumentCreateSerializer, DocumentSerializer
from ..models import Document


class DocumentViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]

    def upload_file(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({}, status=status.HTTP_201_CREATED)

    def get_object(self, version: str):
        return Document.objects.get(file__digest=version, user=self.request.user)

    def get_file_version(
        self, request: Request, version: str, *args, **kwargs
    ) -> Response:
        try:
            instance = self.get_object(version)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(instance)
        return Response(serializer.data)

    def download_file(self, request, file_path):
        try:
            revision = int(request.query_params.get("revision"))
        except ValueError:
            return Response(
                {"detail": "Invalid revision value"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except TypeError:
            revision = None

        documents = Document.objects.filter(
            file_location=file_path, user=self.request.user
        ).order_by("created_at")

        if not documents:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if revision is None:
            document = documents.last()
        else:
            document = documents[revision]

        return FileResponse(document.file.uploaded_file, as_attachment=True)

    def get_files(self, request: Request) -> Response:
        file_location = request.query_params.get("file_location")
        queryset = Document.objects.filter(user=self.request.user)

        if file_location:
            queryset = queryset.filter(file_location=file_location)

        queryset = queryset.order_by("created_at")

        serializer = DocumentSerializer(queryset, many=True)
        data = serializer.data

        if file_location:
            for i, document in enumerate(data):
                document["revision"] = i

        return Response(data)
