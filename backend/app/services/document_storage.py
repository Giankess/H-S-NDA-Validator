from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import os
from datetime import datetime
from ..core.config import settings
import uuid

class DocumentStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the required buckets exist"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
        except S3Error as e:
            print(f"Error creating bucket: {e}")

    def _generate_file_path(self, user_id: str, document_id: str, file_type: str) -> str:
        """Generate a file path for storage"""
        return f"{user_id}/{document_id}/{file_type}.docx"

    async def save_original_document(self, file: UploadFile, user_id: str) -> tuple[str, str]:
        """Save the original uploaded document"""
        document_id = str(uuid.uuid4())
        file_path = self._generate_file_path(user_id, document_id, "original")
        
        # Save the file
        content = await file.read()
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_path,
            data=content,
            length=len(content),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        return document_id, file_path

    def save_redline_document(self, content: bytes, user_id: str, document_id: str) -> str:
        """Save the redline version of the document"""
        file_path = self._generate_file_path(user_id, document_id, "redline")
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_path,
            data=content,
            length=len(content),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        return file_path

    def save_clean_document(self, content: bytes, user_id: str, document_id: str) -> str:
        """Save the clean version of the document"""
        file_path = self._generate_file_path(user_id, document_id, "clean")
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_path,
            data=content,
            length=len(content),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        return file_path

    def get_document(self, file_path: str) -> bytes:
        """Retrieve a document from storage"""
        try:
            response = self.client.get_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=file_path
            )
            return response.read()
        except S3Error as e:
            print(f"Error retrieving document: {e}")
            raise

    def delete_document(self, file_path: str):
        """Delete a document from storage"""
        try:
            self.client.remove_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=file_path
            )
        except S3Error as e:
            print(f"Error deleting document: {e}")
            raise 