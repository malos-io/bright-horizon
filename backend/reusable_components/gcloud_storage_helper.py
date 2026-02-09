import os
import re
from datetime import timedelta
from google.cloud import storage
from google.oauth2 import service_account
from google.auth import default as google_auth_default
from google.auth.transport import requests as google_auth_requests

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Bucket mapping: dev → dev.brighthii.com, staging → staging.brighthii.com, prod → brighthii.com
_BUCKET_MAP = {
    "dev": "dev.brighthii.com",
    "staging": "staging.brighthii.com",
    "prod": "brighthii.com",
}

_client = None


def _get_client():
    global _client
    if _client is None:
        # Dev: use the same creds file as Firebase; Prod: default service account
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brighthii-creds.json")
        if os.path.exists(creds_path):
            creds = service_account.Credentials.from_service_account_file(creds_path)
            _client = storage.Client(credentials=creds, project=creds.project_id)
        else:
            _client = storage.Client()
    return _client


def get_bucket_name() -> str:
    return os.getenv("GCS_BUCKET", _BUCKET_MAP.get(ENVIRONMENT, "dev.brighthii.com"))


def upload_file(file_bytes: bytes, destination_path: str, content_type: str = "application/octet-stream", bucket_name: str = None) -> str:
    """
    Upload a file to GCS and return the public URL.

    Args:
        file_bytes: The file content as bytes.
        destination_path: Path within the bucket (e.g. "assets/logo.png").
        content_type: MIME type of the file.
        bucket_name: Override bucket name. Defaults to environment-based bucket.

    Returns:
        Public URL of the uploaded file.
    """
    client = _get_client()
    bucket = client.bucket(bucket_name or get_bucket_name())
    blob = bucket.blob(destination_path)
    blob.upload_from_string(file_bytes, content_type=content_type)
    return blob.public_url


def upload_from_path(file_path: str, destination_path: str, content_type: str = None, bucket_name: str = None) -> str:
    """
    Upload a local file to GCS and return the public URL.

    Args:
        file_path: Local path to the file.
        destination_path: Path within the bucket (e.g. "assets/logo.png").
        content_type: MIME type. If None, auto-detected.
        bucket_name: Override bucket name. Defaults to environment-based bucket.

    Returns:
        Public URL of the uploaded file.
    """
    client = _get_client()
    bucket = client.bucket(bucket_name or get_bucket_name())
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(file_path, content_type=content_type)
    return blob.public_url


def generate_signed_url(gcs_path: str, expiration_minutes: int = 60, bucket_name: str = None) -> str:
    """Generate a signed URL for a GCS object (time-limited access)."""
    client = _get_client()
    bucket = client.bucket(bucket_name or get_bucket_name())
    blob = bucket.blob(gcs_path)

    # Dev: client has a private key from the creds file, sign locally
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brighthii-creds.json")
    if os.path.exists(creds_path):
        return blob.generate_signed_url(expiration=timedelta(minutes=expiration_minutes), method="GET")

    # Staging/Prod (Cloud Run): no private key, use IAM signBlob API
    credentials, _project = google_auth_default()
    credentials.refresh(google_auth_requests.Request())
    return blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
    )


def delete_file(destination_path: str, bucket_name: str = None):
    """Delete a file from GCS."""
    client = _get_client()
    bucket = client.bucket(bucket_name or get_bucket_name())
    blob = bucket.blob(destination_path)
    blob.delete()


def get_applicant_folder(first_name: str, last_name: str, birthdate: str, middle_name: str = "") -> str:
    """
    Build a folder path for an applicant: LastName_FirstName_MiddleName_YYYY-MM-DD

    Args:
        first_name: Applicant's first name.
        last_name: Applicant's last name.
        birthdate: Birthdate string (YYYY-MM-DD).
        middle_name: Optional middle name.

    Returns:
        Sanitized folder path string (e.g. "Dela_Cruz_Juan_Carlos_1995-03-15").
    """
    parts = [last_name, first_name]
    if middle_name:
        parts.append(middle_name)
    parts.append(birthdate)
    folder = "_".join(parts)
    # Sanitize: keep only alphanumeric, underscores, hyphens
    folder = re.sub(r"[^\w\-]", "_", folder)
    # Collapse multiple underscores
    folder = re.sub(r"_+", "_", folder).strip("_")
    return folder


def upload_applicant_file(file_bytes: bytes, filename: str, first_name: str, last_name: str, birthdate: str, middle_name: str = "", content_type: str = "application/octet-stream", bucket_name: str = None) -> str:
    """
    Upload a file to an applicant's folder and return the public URL.

    Files are stored as: {LastName_FirstName_MiddleName_Birthdate}/{filename}

    Returns:
        Public URL of the uploaded file.
    """
    folder = get_applicant_folder(first_name, last_name, birthdate, middle_name)
    destination_path = f"{folder}/{filename}"
    return upload_file(file_bytes, destination_path, content_type, bucket_name)
