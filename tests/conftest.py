import pytest
from rest_framework.test import APIClient

from propylon_document_manager.file_versions.models import User
from .factories import UserFactory


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture()
def api_client():
    def _api_client(user=None):
        client = APIClient()
        if user:
            client.force_authenticate(user=user)
        return client

    return _api_client
