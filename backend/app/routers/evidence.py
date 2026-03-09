import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.database import DataConsent, EvidenceFile, ImmigrationProfileDB, User
from app.parsers.router import route_parser
from app.services.pii_scrubber import scrub_file_on_disk, scrub_text

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "json", "mbox", "ics", "docx", "jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    profile_id: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file extension
    ext = os.path.splitext(file.filename or "file")[1].lstrip(".")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{ext}' not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Verify consent
    consent_result = await db.execute(
        select(DataConsent).where(
            DataConsent.user_id == user.id,
            DataConsent.source_type == source_type,
            DataConsent.consent_given == True,
            DataConsent.revoked_at.is_(None),
        )
    )
    if not consent_result.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail=f"No consent given for source: {source_type}. Please provide consent before uploading.",
        )

    # Verify profile ownership
    profile_result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse
    try:
        parsed = route_parser(ext, source_type, file_path)
        extracted_text = parsed.get("text", str(parsed))
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {str(e)}")

    # Scrub PII from extracted text and file on disk
    extracted_text = scrub_text(extracted_text)
    scrub_file_on_disk(file_path, source_type)

    # Store record
    evidence = EvidenceFile(
        profile_id=profile.id,
        filename=file.filename or "unknown",
        file_type=ext,
        source_type=source_type,
        file_path=file_path,
        extracted_text=extracted_text[:50000],
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)

    return {
        "id": str(evidence.id),
        "filename": evidence.filename,
        "source_type": source_type,
        "extracted_preview": extracted_text[:500],
    }


@router.get("/{profile_id}")
async def list_evidence(
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify profile ownership
    profile_result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    if not profile_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await db.execute(
        select(EvidenceFile).where(EvidenceFile.profile_id == profile_id)
    )
    files = result.scalars().all()
    return [
        {
            "id": str(f.id),
            "filename": f.filename,
            "file_type": f.file_type,
            "source_type": f.source_type,
            "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
            "extracted_preview": (f.extracted_text or "")[:300],
        }
        for f in files
    ]


@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EvidenceFile).where(EvidenceFile.id == evidence_id)
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Verify ownership via profile
    profile_result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == evidence.profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    if not profile_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Delete file from disk
    if evidence.file_path and os.path.exists(evidence.file_path):
        os.remove(evidence.file_path)

    await db.delete(evidence)
    await db.commit()
    return {"deleted": True}
