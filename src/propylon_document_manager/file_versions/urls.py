from django.urls import path

from propylon_document_manager.file_versions.api.views import DocumentViewSet

urlpatterns = [
    path(
        "documents",
        DocumentViewSet.as_view({"post": "upload_file", "get": "get_files"}),
        name="document",
    ),
    path(
        "documents/<str:version>",
        DocumentViewSet.as_view({"get": "get_file_version"}),
        name="get-file-version",
    ),
    path(
        "documents/<path:file_path>",
        DocumentViewSet.as_view({"get": "download_file"}),
        name="download-file",
    ),
]
