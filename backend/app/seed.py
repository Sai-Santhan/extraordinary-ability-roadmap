#!/usr/bin/env python3
"""Seed the database with synthetic demo personas."""
import asyncio
import os
import shutil

from sqlalchemy import select

from app.auth import hash_password
from app.database import async_session, init_db
from app.models.database import DataConsent, EvidenceFile, ImmigrationProfileDB, User

SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "synthetic-data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

PERSONAS = [
    {
        "name": "Dr. Priya Sharma",
        "email": "priya@demo.com",
        "password": "demo1234",
        "dir": "priya-sharma",
        "files": [
            {"filename": "cv.txt", "file_type": "txt", "source_type": "cv"},
            {"filename": "scholar.json", "file_type": "json", "source_type": "scholar"},
            {"filename": "gmail.mbox", "file_type": "mbox", "source_type": "gmail"},
            {"filename": "calendar.ics", "file_type": "ics", "source_type": "calendar"},
        ],
    },
    {
        "name": "Marco Chen",
        "email": "marco@demo.com",
        "password": "demo1234",
        "dir": "marco-chen",
        "files": [
            {"filename": "cv.txt", "file_type": "txt", "source_type": "cv"},
            {"filename": "github.json", "file_type": "json", "source_type": "github"},
            {"filename": "linkedin.txt", "file_type": "txt", "source_type": "linkedin"},
        ],
    },
    {
        "name": "Amara Okafor",
        "email": "amara@demo.com",
        "password": "demo1234",
        "dir": "amara-okafor",
        "files": [
            {"filename": "cv.txt", "file_type": "txt", "source_type": "cv"},
            {"filename": "linkedin.txt", "file_type": "txt", "source_type": "linkedin"},
            {"filename": "chatgpt-export.json", "file_type": "json", "source_type": "chatgpt_export"},
            {"filename": "media-urls.json", "file_type": "json", "source_type": "manual"},
        ],
    },
]


async def seed():
    await init_db()

    async with async_session() as db:
        for persona in PERSONAS:
            # Check if user already exists
            existing = await db.execute(
                select(User).where(User.email == persona["email"])
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping {persona['name']} (already exists)")
                continue

            # Create user
            user = User(
                email=persona["email"],
                hashed_password=hash_password(persona["password"]),
                name=persona["name"],
            )
            db.add(user)
            await db.flush()

            # Create consents for each source type
            source_types = set(f["source_type"] for f in persona["files"])
            for source_type in source_types:
                consent = DataConsent(
                    user_id=user.id,
                    source_type=source_type,
                    consent_given=True,
                    processing_description=f"Demo consent for {source_type}",
                )
                db.add(consent)

            # Create profile
            profile = ImmigrationProfileDB(user_id=user.id, status="created")
            db.add(profile)
            await db.flush()

            # Copy files and create evidence records
            persona_dir = os.path.join(SYNTHETIC_DIR, persona["dir"])
            for file_info in persona["files"]:
                src_path = os.path.join(persona_dir, file_info["filename"])
                if not os.path.exists(src_path):
                    print(f"  Warning: {src_path} not found, skipping")
                    continue

                # Copy to uploads
                dest_filename = f"{user.id}_{file_info['filename']}"
                dest_path = os.path.join(UPLOAD_DIR, dest_filename)
                shutil.copy2(src_path, dest_path)

                evidence = EvidenceFile(
                    profile_id=profile.id,
                    filename=file_info["filename"],
                    file_type=file_info["file_type"],
                    source_type=file_info["source_type"],
                    file_path=dest_path,
                )
                db.add(evidence)

            await db.commit()
            print(f"  Created: {persona['name']} ({persona['email']}) with {len(persona['files'])} files")

    print("\nSeed complete! Demo accounts:")
    for p in PERSONAS:
        print(f"  {p['email']} / {p['password']}")


if __name__ == "__main__":
    asyncio.run(seed())
