import hashlib
from io import BytesIO


def get_file_digest(file: BytesIO) -> str:
    digest = hashlib.file_digest(file, "md5")
    return digest.hexdigest()
