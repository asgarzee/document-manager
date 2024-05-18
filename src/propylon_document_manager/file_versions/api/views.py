from typing import Any

from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import FileVersionSerializer, DocumentCreateSerializer
from ..models import FileVersion, Document


class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"


class DocumentViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = DocumentCreateSerializer
    queryset = Document.objects.all()

    def get_queryset(self):
        return Document.objects.all()

    def create(self, request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save(user=request.user)
        return Response({}, status=status.HTTP_201_CREATED)
