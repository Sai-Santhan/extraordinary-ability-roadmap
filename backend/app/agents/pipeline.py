import json
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.assessment import AssessmentAgent
from app.agents.extraction import ExtractionAgent
from app.agents.ingestion import IngestionAgent
from app.agents.roadmap import RoadmapAgent
from app.models.database import EvidenceFile, ImmigrationProfileDB
from app.prompts.shared import PATHWAY_DISPLAY


async def run_pipeline(profile_id: str, db: AsyncSession) -> AsyncGenerator[dict, None]:
    result = await db.execute(
        select(ImmigrationProfileDB).where(ImmigrationProfileDB.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        yield {"event": "error", "data": {"message": "Profile not found"}}
        return

    evidence_result = await db.execute(
        select(EvidenceFile).where(EvidenceFile.profile_id == profile_id)
    )
    evidence_files = evidence_result.scalars().all()

    if not evidence_files:
        yield {"event": "error", "data": {"message": "No evidence files uploaded"}}
        return

    ef_dicts = [
        {"file_type": ef.file_type, "source_type": ef.source_type,
         "file_path": ef.file_path, "filename": ef.filename}
        for ef in evidence_files
    ]

    # Agent 1: Ingestion
    yield {"event": "stage", "data": {"stage": "ingestion", "status": "started"}}
    profile.status = "ingesting"
    await db.commit()

    try:
        ingestion_agent = IngestionAgent()
        raw_data = await ingestion_agent.run(ef_dicts)
        profile.raw_career_data = raw_data.model_dump(mode="json")
        await db.commit()
    except Exception as e:
        yield {"event": "stage", "data": {"stage": "ingestion", "status": "error", "message": str(e)}}
        yield {"event": "error", "data": {"message": f"Ingestion failed: {e}"}}
        return
    yield {"event": "stage", "data": {"stage": "ingestion", "status": "completed", "files_processed": raw_data.total_files_processed}}

    # Agent 2: Extraction
    yield {"event": "stage", "data": {"stage": "extraction", "status": "started"}}
    profile.status = "extracting"
    await db.commit()

    try:
        extraction_agent = ExtractionAgent()
        profile_data = await extraction_agent.run(raw_career_data_json=raw_data.model_dump_json())
        profile.profile_data = profile_data
        await db.commit()
    except Exception as e:
        yield {"event": "stage", "data": {"stage": "extraction", "status": "error", "message": str(e)}}
        yield {"event": "error", "data": {"message": f"Extraction failed: {e}"}}
        return
    yield {"event": "stage", "data": {"stage": "extraction", "status": "completed"}}

    # Agent 3: Assessment
    yield {"event": "stage", "data": {"stage": "assessment", "status": "started"}}
    profile.status = "assessing"
    await db.commit()

    try:
        assessment_agent = AssessmentAgent()
        pathway_raw = profile_data.get("target_pathway", "eb1a")
        pathway = PATHWAY_DISPLAY.get(pathway_raw, pathway_raw.upper())
        assessment_data = await assessment_agent.run(
            profile_json=json.dumps(profile_data),
            pathway=pathway,
        )
        profile.assessment_data = assessment_data
        await db.commit()
    except Exception as e:
        yield {"event": "stage", "data": {"stage": "assessment", "status": "error", "message": str(e)}}
        yield {"event": "error", "data": {"message": f"Assessment failed: {e}"}}
        return
    yield {"event": "stage", "data": {"stage": "assessment", "status": "completed"}}

    # Agent 4: Roadmap
    yield {"event": "stage", "data": {"stage": "roadmap", "status": "started"}}
    profile.status = "roadmapping"
    await db.commit()

    try:
        roadmap_agent = RoadmapAgent()
        roadmap_data = await roadmap_agent.run(
            assessment_json=json.dumps(assessment_data),
            name=profile_data.get("name", "Applicant"),
            field=profile_data.get("field_of_expertise", "Technology"),
            pathway=pathway,
            timeline_years=profile_data.get("target_timeline_years", 2),
            strongest=str(assessment_data.get("strongest_criteria", [])),
            weakest=str(assessment_data.get("weakest_criteria", [])),
            focus=str(assessment_data.get("recommended_focus", [])),
            profile_id=str(profile_id),
        )
        profile.roadmap_data = roadmap_data
        profile.status = "complete"
        await db.commit()
    except Exception as e:
        yield {"event": "stage", "data": {"stage": "roadmap", "status": "error", "message": str(e)}}
        yield {"event": "error", "data": {"message": f"Roadmap generation failed: {e}"}}
        return
    yield {"event": "stage", "data": {"stage": "roadmap", "status": "completed"}}
    yield {"event": "complete", "data": {"profile_id": str(profile_id)}}
