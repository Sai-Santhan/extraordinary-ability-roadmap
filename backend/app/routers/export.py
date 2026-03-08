from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.auth import get_current_user
from app.database import get_db
from app.models.database import ImmigrationProfileDB, User
from app.export.markdown import export_markdown
from app.export.pdf import export_pdf
from app.export.docx_export import export_docx

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{profile_id}")
async def export_profile(
    profile_id: str,
    format: str = Query("json", pattern="^(json|markdown|pdf|docx)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImmigrationProfileDB).where(
            ImmigrationProfileDB.id == profile_id,
            ImmigrationProfileDB.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile.profile_data or {}
    assessment_data = profile.assessment_data or {}
    roadmap_data = profile.roadmap_data or {}

    if format == "json":
        content = json.dumps({
            "profile": profile_data,
            "assessment": assessment_data,
            "roadmap": roadmap_data,
            "disclaimer": "This is not legal advice. Consult a qualified immigration attorney.",
        }, indent=2)
        return Response(content=content, media_type="application/json",
                       headers={"Content-Disposition": f"attachment; filename=immigration-profile-{profile_id}.json"})

    elif format == "markdown":
        content = export_markdown(profile_data, assessment_data, roadmap_data)
        return Response(content=content, media_type="text/markdown",
                       headers={"Content-Disposition": f"attachment; filename=immigration-profile-{profile_id}.md"})

    elif format == "pdf":
        content = export_pdf(profile_data, assessment_data, roadmap_data)
        return Response(content=content, media_type="application/pdf",
                       headers={"Content-Disposition": f"attachment; filename=immigration-profile-{profile_id}.pdf"})

    elif format == "docx":
        content = export_docx(profile_data, assessment_data, roadmap_data)
        return Response(content=content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       headers={"Content-Disposition": f"attachment; filename=immigration-profile-{profile_id}.docx"})
