import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON, Uuid as _SAUuid

# Store as CHAR(32) — works on both PostgreSQL and SQLite
Uuid = _SAUuid(as_uuid=False, native_uuid=False)


def _uuid_str():
    return str(uuid.uuid4())
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=_uuid_str)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    onboarding_completed = Column(Boolean, default=False)
    onboarding_data = Column(JSON, nullable=True)

    profiles = relationship("ImmigrationProfileDB", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("DataConsent", back_populates="user", cascade="all, delete-orphan")


class DataConsent(Base):
    __tablename__ = "data_consents"

    id = Column(Uuid, primary_key=True, default=_uuid_str)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False)
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    processing_description = Column(Text, nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="consents")


class ImmigrationProfileDB(Base):
    __tablename__ = "immigration_profiles"

    id = Column(Uuid, primary_key=True, default=_uuid_str)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_data = Column(JSON, nullable=True)
    raw_career_data = Column(JSON, nullable=True)
    assessment_data = Column(JSON, nullable=True)
    roadmap_data = Column(JSON, nullable=True)
    target_pathway = Column(String(10), nullable=True)
    pathway_changed_since_analysis = Column(Boolean, default=False)
    last_pathway_switch = Column(DateTime(timezone=True), nullable=True)
    last_analysis_run = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="created")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="profiles")
    evidence_files = relationship("EvidenceFile", back_populates="profile", cascade="all, delete-orphan")


class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    id = Column(Uuid, primary_key=True, default=_uuid_str)
    profile_id = Column(Uuid, ForeignKey("immigration_profiles.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    source_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=utcnow)

    profile = relationship("ImmigrationProfileDB", back_populates="evidence_files")
