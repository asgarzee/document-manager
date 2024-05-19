from io import BytesIO

from propylon_document_manager.file_versions.utils import get_file_digest


def test_get_file_digest(mocker):
    mock_file_digest = mocker.patch(
        "propylon_document_manager.file_versions.utils.hashlib.file_digest"
    )
    stream = BytesIO(b"dummy text")

    result = get_file_digest(stream)

    assert result == mock_file_digest.return_value.hexdigest.return_value
    mock_file_digest.assert_called_once_with(stream, "md5")
