"""
SB1/US7 - Resume Upload, Listing, Download and Management Endpoints
"""
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from backend.db.database import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.schemas.resume import ResumeResponse
from backend.auth.jwt import get_current_user
from backend.services.file_storage import file_storage_service

router = APIRouter(prefix="/api/v1/resume", tags=["Resume Management"])

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    metadata = await file_storage_service.save_resume(file, current_user.id)

    # Mark existing resumes as non-primary
    await db.execute(
        update(Resume)
        .where(Resume.user_id == current_user.id)
        .values(is_primary=False)
    )

    resume_entry = Resume(
        user_id=current_user.id,
        filename=metadata["filename"],
        file_path=metadata["file_path"],
        file_size=metadata["file_size"],
        mime_type=metadata["mime_type"],
        is_primary=True
    )
    db.add(resume_entry)
    await db.commit()
    await db.refresh(resume_entry)
    return resume_entry

@router.get("", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()

@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk.")

    return FileResponse(
        path=resume.file_path,
        filename=resume.filename,
        media_type=resume.mime_type
    )

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    file_storage_service.delete_file(resume.file_path)
    await db.delete(resume)
    await db.commit()
    return {"message": "Resume deleted successfully."}
