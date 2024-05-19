import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from rest_framework import status

from propylon_document_manager.file_versions.models import Document, File
from propylon_document_manager.file_versions.utils import get_file_digest
from tests.factories import UserFactory


@pytest.mark.django_db
class TestUploadFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = "/api/documents"

    @pytest.mark.parametrize("file_type", (".pdf", ".txt", ".csv"))
    def test_upload_file(self, user, api_client, file_type):
        with NamedTemporaryFile(mode="w+b", suffix=file_type, delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"infra/{file_name}"

            payload = {"file_location": file_location, "upload_file": file}

            response = api_client(user).post(
                path=self.url, data=payload, format="multipart"
            )

        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["file_location"] == file_location

        document = Document.objects.get(
            file_location=file_location, user=user, file__file_name=file_name
        )

        assert document.file_location == file_location
        assert document.user == user
        assert document.file.file_name == file_name

    @pytest.mark.parametrize(
        "file_location, error_msg",
        (
            ("/dummy/place.pdf", "Leading and trailing forward slashes not permitted"),
            (
                "dummy/dummyfile.pdf/",
                "Leading and trailing forward slashes not permitted",
            ),
        ),
    )
    def test_upload_file_with_invalid_data(
        self, user, api_client, file_location, error_msg
    ):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)

            payload = {"file_location": file_location, "upload_file": file}

            response = api_client(user).post(
                path=self.url, data=payload, format="multipart"
            )

        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["file_location"] == [error_msg]

    def test_upload_file_with_file_location_file_name_different(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)

            payload = {"file_location": "dummy/dummy-file.pdf", "upload_file": file}

            response = api_client(user).post(
                path=self.url, data=payload, format="multipart"
            )

        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["non_field_errors"] == [
            "file_location filename must be same as the upload file"
        ]


@pytest.mark.django_db
class TestDownloadFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = "/api/documents"

    def test_download_file(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest = get_file_digest(file)
            file_path = Path(digest) / file_name

            file_obj = File.objects.create(file_name=file_name, digest=digest)
            file_obj.uploaded_file.save(file_path.as_posix(), file)

            Document.objects.create(
                file=file_obj, user=user, file_location=file_location
            )

            response = api_client(user).get(f"{self.url}/{file_location}")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{file_name}"'
        )

    def test_download_file_of_different_user(self, user, api_client):
        current_user = UserFactory()
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest = get_file_digest(file)
            file_path = Path(digest) / file_name

            file_obj = File.objects.create(file_name=file_name, digest=digest)
            file_obj.uploaded_file.save(file_path.as_posix(), file)
            Document.objects.create(
                file=file_obj, user=user, file_location=file_location
            )

            response = api_client(current_user).get(f"{self.url}/{file_location}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_file_original_file(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest_1 = get_file_digest(file)
            file_path_1 = Path(digest_1) / file_name

            file_obj_1 = File.objects.create(file_name=file_name, digest=digest_1)
            file_obj_1.uploaded_file.save(file_path_1.as_posix(), file)

            Document.objects.create(
                file=file_obj_1, user=user, file_location=file_location
            )

            file.write(b"new dummy data")
            file.seek(0)
            digest_2 = get_file_digest(file)
            file_path_2 = Path(digest_2) / file_name
            file_obj_2 = File.objects.create(file_name=file_name, digest=digest_2)
            file_obj_2.uploaded_file.save(file_path_2.as_posix(), file)

            Document.objects.create(
                file=file_obj_2, user=user, file_location=file_location
            )

            response = api_client(user).get(f"{self.url}/{file_location}?revision=0")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{file_name}"'
        )
        assert hashlib.md5(response.getvalue()).hexdigest() == digest_1

    def test_download_file_using_version(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest_1 = get_file_digest(file)
            file_path_1 = Path(digest_1) / file_name

            file_obj_1 = File.objects.create(file_name=file_name, digest=digest_1)
            file_obj_1.uploaded_file.save(file_path_1.as_posix(), file)

            Document.objects.create(
                file=file_obj_1, user=user, file_location=file_location
            )

            file.write(b"new dummy data")
            file.seek(0)
            digest_2 = get_file_digest(file)
            file_path_2 = Path(digest_2) / file_name
            file_obj_2 = File.objects.create(file_name=file_name, digest=digest_2)
            file_obj_2.uploaded_file.save(file_path_2.as_posix(), file)

            Document.objects.create(
                file=file_obj_2, user=user, file_location=file_location
            )

            response = api_client(user).get(
                f"{self.url}/{file_location}?version={digest_2}"
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{file_name}"'
        )
        assert hashlib.md5(response.getvalue()).hexdigest() == digest_2

    def test_download_file_latest_file_without_revision(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest_1 = get_file_digest(file)
            file_path_1 = Path(digest_1) / file_name

            file_obj_1 = File.objects.create(file_name=file_name, digest=digest_1)
            file_obj_1.uploaded_file.save(file_path_1.as_posix(), file)

            Document.objects.create(
                file=file_obj_1, user=user, file_location=file_location
            )

            file.write(b"new dummy data")
            file.seek(0)
            digest_2 = get_file_digest(file)
            file_path_2 = Path(digest_2) / file_name
            file_obj_2 = File.objects.create(file_name=file_name, digest=digest_2)
            file_obj_2.uploaded_file.save(file_path_2.as_posix(), file)

            Document.objects.create(
                file=file_obj_2, user=user, file_location=file_location
            )

            response = api_client(user).get(f"{self.url}/{file_location}")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{file_name}"'
        )
        assert hashlib.md5(response.getvalue()).hexdigest() == digest_2

    def test_download_file_when_revision_and_version_both_provided(
        self, user, api_client
    ):
        response = api_client(user).get(
            f"{self.url}/dummy/data.pdf?revision=1&version=d2b32a4f3a"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"] == "Provide either version or revision"

    def test_download_file_with_invalida_revision_value(self, user, api_client):
        response = api_client(user).get(f"{self.url}/dummy/data.pdf?revision=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"] == "Invalid revision value"

    def test_download_file_does_not_exist(self, user, api_client):
        response = api_client(user).get(f"{self.url}/dummy/data.pdf")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_file_with_unauthenticated_user(self, api_client):
        response = api_client().get(f"{self.url}/dummy/data.pdf")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetFiles:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = "/api/documents"

    def test_get_files(self, user, api_client):
        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest_1 = get_file_digest(file)
            file_path_1 = Path(digest_1) / file_name

            file_obj_1 = File.objects.create(file_name=file_name, digest=digest_1)
            file_obj_1.uploaded_file.save(file_path_1.as_posix(), file)

            Document.objects.create(
                file=file_obj_1, user=user, file_location=file_location
            )

            file.write(b"new dummy data")
            file.seek(0)
            digest_2 = get_file_digest(file)
            file_path_2 = Path(digest_2) / file_name
            file_obj_2 = File.objects.create(file_name=file_name, digest=digest_2)
            file_obj_2.uploaded_file.save(file_path_2.as_posix(), file)

            Document.objects.create(
                file=file_obj_2, user=user, file_location=file_location
            )

            response = api_client(user).get(self.url)

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 2
        assert data[0]["file_url"] == f"/api/documents/{file_location}"
        assert data[1]["file_url"] == f"/api/documents/{file_location}"
        assert data[0]["file_location"] == file_location
        assert data[1]["file_location"] == file_location
        assert data[0]["version"] == digest_1
        assert data[1]["version"] == digest_2

    def test_get_files_of_different_user(self, user, api_client):
        current_user = UserFactory()

        with NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=True) as file:
            file.write(b"test file body")
            file.seek(0)
            file_name = file.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest = get_file_digest(file)
            file_path = Path(digest) / file_name

            file_obj = File.objects.create(file_name=file_name, digest=digest)
            file_obj.uploaded_file.save(file_path.as_posix(), file)
            Document.objects.create(
                file=file_obj, user=user, file_location=file_location
            )

            response = api_client(current_user).get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_files_with_file_location(self, user, api_client):
        with NamedTemporaryFile(
            mode="w+b", suffix=".pdf", delete=True
        ) as file_1, NamedTemporaryFile(
            mode="w+b", suffix=".txt", delete=True
        ) as text_file:
            file_1.write(b"test file body")
            file_1.seek(0)
            file_name = file_1.name.split("/")[-1]
            file_location = f"dummy/{file_name}"
            digest_1 = get_file_digest(file_1)
            file_path_1 = Path(digest_1) / file_name

            file_obj_1 = File.objects.create(file_name=file_name, digest=digest_1)
            file_obj_1.uploaded_file.save(file_path_1.as_posix(), file_1)

            Document.objects.create(
                file=file_obj_1, user=user, file_location=file_location
            )

            file_1.write(b"new dummy data")
            file_1.seek(0)
            digest_2 = get_file_digest(file_1)
            file_path_2 = Path(digest_2) / file_name
            file_obj_2 = File.objects.create(file_name=file_name, digest=digest_2)
            file_obj_2.uploaded_file.save(file_path_2.as_posix(), file_1)

            Document.objects.create(
                file=file_obj_2, user=user, file_location=file_location
            )

            text_file.write(b"new dummy file for testing ")
            text_file.seek(0)
            text_file_name = text_file.name.split("/")[-1]
            text_file_location = f"dummy_text_file/{file_name}"
            text_file_digest = get_file_digest(text_file)
            text_file_path = Path(text_file_digest) / file_name

            text_file_obj = File.objects.create(
                file_name=text_file_name, digest=text_file_digest
            )
            text_file_obj.uploaded_file.save(text_file_path.as_posix(), text_file)

            Document.objects.create(
                file=text_file_obj, user=user, file_location=text_file_location
            )

            response = api_client(user).get(f"{self.url}?file-location={file_location}")

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 2
        assert data[0]["revision"] == 0
        assert data[1]["revision"] == 1
        assert data[0]["file_url"] == f"/api/documents/{file_location}"
        assert data[1]["file_url"] == f"/api/documents/{file_location}"
        assert data[0]["file_location"] == file_location
        assert data[1]["file_location"] == file_location
        assert data[0]["version"] == digest_1
        assert data[1]["version"] == digest_2
