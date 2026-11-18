"""
SB1/US7 - Secure File Storage Service for Resumes and Documents
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from backend.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"
}

class FileStorageService:
    def __init__(self):
        self.upload_dir = os.path.abspath(os.path.join(settings.upload_dir, "resumes"))
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_resume(self, file: UploadFile, user_id: str) -> dict:
        filename = file.filename or "resume.pdf"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension {ext}. Only PDF and DOCX files are permitted."
            )

        # Generate unique storage filename to avoid collisions
        unique_name = f"{user_id}_{uuid.uuid4().hex[:10]}{ext}"
        target_path = os.path.join(self.upload_dir, unique_name)

        content = await file.read()
        size = len(content)
        max_bytes = settings.max_resume_size_mb * 1024 * 1024

        if size > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {settings.max_resume_size_mb}MB."
            )

        async with aiofiles.open(target_path, "wb") as out_f:
            await out_f.write(content)

        return {
            "filename": filename,
            "file_path": target_path,
            "file_size": size,
            "mime_type": file.content_type or "application/octet-stream"
        }

    def delete_file(self, file_path: str) -> bool:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False

file_storage_service = FileStorageService()
