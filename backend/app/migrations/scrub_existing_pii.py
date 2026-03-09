"""One-time migration to scrub contact-level PII from existing database records and files on disk.

Usage: cd backend && .venv/bin/python -m app.migrations.scrub_existing_pii
"""

import asyncio
import json

from sqlalchemy import select, update

from app.database import async_session, init_db
from app.models.database import EvidenceFile, ImmigrationProfileDB
from app.services.pii_scrubber import (
    scrub_file_on_disk,
    scrub_json_strings,
    scrub_text,
)


async def scrub_evidence_files():
    """Scrub extracted_text and files on disk for all evidence records."""
    async with async_session() as db:
        result = await db.execute(select(EvidenceFile))
        files = result.scalars().all()
        count = 0
        for ef in files:
            changed = False

            # Scrub extracted text in DB
            if ef.extracted_text:
                scrubbed = scrub_text(ef.extracted_text)
                if scrubbed != ef.extracted_text:
                    ef.extracted_text = scrubbed
                    changed = True

            # Scrub file on disk
            if ef.file_path:
                scrub_file_on_disk(ef.file_path, ef.source_type or "")

            if changed:
                count += 1

        await db.commit()
        print(f"  Scrubbed {count} evidence file records")


async def scrub_profiles():
    """Scrub raw_career_data, assessment_data, and roadmap_data for all profiles."""
    async with async_session() as db:
        result = await db.execute(select(ImmigrationProfileDB))
        profiles = result.scalars().all()
        count = 0
        for profile in profiles:
            changed = False

            # Scrub raw_career_data (contains raw_text per source)
            if profile.raw_career_data and isinstance(profile.raw_career_data, dict):
                sources = profile.raw_career_data.get("sources", [])
                for source in sources:
                    if "raw_text" in source and source["raw_text"]:
                        scrubbed = scrub_text(source["raw_text"])
                        if scrubbed != source["raw_text"]:
                            source["raw_text"] = scrubbed
                            changed = True
                if changed:
                    # Force SQLAlchemy to detect the change
                    profile.raw_career_data = {**profile.raw_career_data}

            # Scrub assessment_data (Claude may have echoed PII in evidence_found strings)
            if profile.assessment_data and isinstance(profile.assessment_data, dict):
                scrubbed = scrub_json_strings(profile.assessment_data)
                if scrubbed != profile.assessment_data:
                    profile.assessment_data = scrubbed
                    changed = True

            # Scrub roadmap_data (narrative_summary may contain PII)
            if profile.roadmap_data and isinstance(profile.roadmap_data, dict):
                scrubbed = scrub_json_strings(profile.roadmap_data)
                if scrubbed != profile.roadmap_data:
                    profile.roadmap_data = scrubbed
                    changed = True

            if changed:
                count += 1

        await db.commit()
        print(f"  Scrubbed {count} profile records")


async def main():
    print("Initializing database connection...")
    await init_db()

    print("Scrubbing evidence files...")
    await scrub_evidence_files()

    print("Scrubbing immigration profiles...")
    await scrub_profiles()

    print("PII scrubbing migration complete.")


if __name__ == "__main__":
    asyncio.run(main())
