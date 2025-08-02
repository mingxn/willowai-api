from minio import Minio
from src.config import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False  # Use True for HTTPS
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        bucket_name = settings.MINIO_BUCKET_NAME
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)

    def put_object(self, object_name: str, data: bytes, length: int, content_type: str):
        return self.client.put_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
            data,
            length,
            content_type
        )

    def get_object(self, object_name: str):
        return self.client.get_object(
            settings.MINIO_BUCKET_NAME,
            object_name
        )

    def delete_object(self, object_name: str):
        return self.client.remove_object(
            settings.MINIO_BUCKET_NAME,
            object_name
        )

# Initialize the Minio client instance
minio_client = MinioClient()
