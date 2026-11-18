"""
SB1/US8 - Academic Records Management and CSV Bulk Import
"""
import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.db.database import get_db
from backend.models.user import User
from backend.models.academics import AcademicRecord
from backend.schemas.academics import AcademicCreate, AcademicResponse
from backend.auth.jwt import get_current_user

router = APIRouter(prefix="/api/v1/academics", tags=["Academic Records"])

@router.get("", response_model=List[AcademicResponse])
async def list_academics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    return (await db.execute(stmt)).scalars().all()

@router.post("", response_model=AcademicResponse, status_code=status.HTTP_201_CREATED)
async def add_academic_record(
    record_in: AcademicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rec = AcademicRecord(
        user_id=current_user.id,
        institution=record_in.institution.strip(),
        degree=record_in.degree.strip(),
        field_of_study=record_in.field_of_study.strip(),
        cgpa=record_in.cgpa,
        start_year=record_in.start_year,
        end_year=record_in.end_year,
        is_current=record_in.is_current or False
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec

@router.post("/import", response_model=List[AcademicResponse])
async def import_academics_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    try:
        text_data = content.decode("utf-8")
    except Exception:
        text_data = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text_data))
    created = []
    for row in reader:
        try:
            inst = row.get("institution") or row.get("Institution") or "University"
            deg = row.get("degree") or row.get("Degree") or "Bachelor"
            field = row.get("field_of_study") or row.get("Field") or "Computer Science"
            cgpa_val = float(row.get("cgpa", 0.0) or row.get("CGPA", 0.0) or 0.0)
            start_yr = int(row.get("start_year", 2022) or 2022)
            end_yr = int(row.get("end_year", 2026) or 2026)

            rec = AcademicRecord(
                user_id=current_user.id,
                institution=inst.strip(),
                degree=deg.strip(),
                field_of_study=field.strip(),
                cgpa=cgpa_val,
                start_year=start_yr,
                end_year=end_yr,
                is_current=False
            )
            db.add(rec)
            created.append(rec)
        except Exception:
            continue

    if created:
        await db.commit()
        for r in created:
            await db.refresh(r)

    return created

@router.delete("/{record_id}")
async def delete_academic_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AcademicRecord).where(AcademicRecord.id == record_id, AcademicRecord.user_id == current_user.id)
    rec = (await db.execute(stmt)).scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Academic record not found.")
    await db.delete(rec)
    await db.commit()
    return {"message": "Academic record removed."}
