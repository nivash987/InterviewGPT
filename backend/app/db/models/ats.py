from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AtsAnalysis(Base):
    __tablename__ = "ats_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ats_score: Mapped[int] = mapped_column(Integer, nullable=False)
    completeness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    section_scores: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    skills_found: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    missing_skills: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    keyword_coverage: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    strengths: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    weaknesses: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    suggestions: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    recommended_roles: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SkillTaxonomy(Base):
    __tablename__ = "skill_taxonomy"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JobProfile(Base):
    __tablename__ = "job_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    required_skills: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    preferred_skills: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
