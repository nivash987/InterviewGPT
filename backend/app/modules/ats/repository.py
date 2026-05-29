from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.ats import AtsAnalysis, JobProfile, SkillTaxonomy
from app.db.models.resume import Resume
from app.modules.ats.analyzer import JobProfileData
from app.modules.ats.schemas import (
    AtsAnalysisPublic,
    AtsHistoryItem,
    KeywordCoverage,
    RecommendedRole,
    SectionScores,
)


class AtsRepository(ABC):
    @abstractmethod
    async def create_analysis(
        self,
        *,
        user_id: str,
        resume_id: str,
        ats_score: int,
        completeness_score: int,
        section_scores: dict,
        skills_found: list[str],
        missing_skills: list[str],
        keyword_coverage: dict,
        strengths: list[str],
        weaknesses: list[str],
        suggestions: list[str],
        recommended_roles: list[dict],
    ) -> AtsAnalysis: ...

    @abstractmethod
    async def get_latest_for_resume(
        self,
        *,
        user_id: str,
        resume_id: str,
    ) -> AtsAnalysis | None: ...

    @abstractmethod
    async def list_history_for_user(self, *, user_id: str) -> list[tuple[AtsAnalysis, str | None]]: ...

    @abstractmethod
    async def list_taxonomy_skills(self) -> list[str]: ...

    @abstractmethod
    async def list_job_profiles(self) -> list[JobProfileData]: ...


def _analysis_to_public(analysis: AtsAnalysis) -> AtsAnalysisPublic:
    return AtsAnalysisPublic(
        id=str(analysis.id),
        resume_id=str(analysis.resume_id),
        ats_score=analysis.ats_score,
        completeness_score=analysis.completeness_score,
        section_scores=SectionScores.model_validate(analysis.section_scores),
        skills_found=list(analysis.skills_found),
        missing_skills=list(analysis.missing_skills),
        keyword_coverage=KeywordCoverage.model_validate(analysis.keyword_coverage),
        strengths=list(analysis.strengths),
        weaknesses=list(analysis.weaknesses),
        suggestions=list(analysis.suggestions),
        recommended_roles=[RecommendedRole.model_validate(r) for r in analysis.recommended_roles],
        created_at=analysis.created_at,
    )


class SqlAlchemyAtsRepository(AtsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_analysis(
        self,
        *,
        user_id: str,
        resume_id: str,
        ats_score: int,
        completeness_score: int,
        section_scores: dict,
        skills_found: list[str],
        missing_skills: list[str],
        keyword_coverage: dict,
        strengths: list[str],
        weaknesses: list[str],
        suggestions: list[str],
        recommended_roles: list[dict],
    ) -> AtsAnalysis:
        analysis = AtsAnalysis(
            user_id=uuid.UUID(user_id),
            resume_id=uuid.UUID(resume_id),
            ats_score=ats_score,
            completeness_score=completeness_score,
            section_scores=section_scores,
            skills_found=skills_found,
            missing_skills=missing_skills,
            keyword_coverage=keyword_coverage,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            recommended_roles=recommended_roles,
        )
        self._session.add(analysis)
        await self._session.flush()
        return analysis

    async def get_latest_for_resume(
        self,
        *,
        user_id: str,
        resume_id: str,
    ) -> AtsAnalysis | None:
        stmt = (
            select(AtsAnalysis)
            .where(
                AtsAnalysis.user_id == uuid.UUID(user_id),
                AtsAnalysis.resume_id == uuid.UUID(resume_id),
            )
            .order_by(AtsAnalysis.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_history_for_user(self, *, user_id: str) -> list[tuple[AtsAnalysis, str | None]]:
        stmt = (
            select(AtsAnalysis, Resume.title)
            .join(Resume, Resume.id == AtsAnalysis.resume_id)
            .where(AtsAnalysis.user_id == uuid.UUID(user_id))
            .order_by(AtsAnalysis.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_taxonomy_skills(self) -> list[str]:
        stmt = select(SkillTaxonomy.skill_name).order_by(SkillTaxonomy.skill_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_job_profiles(self) -> list[JobProfileData]:
        stmt = select(JobProfile).order_by(JobProfile.role_name)
        result = await self._session.execute(stmt)
        profiles = result.scalars().all()
        return [
            JobProfileData(
                role_name=p.role_name,
                required_skills=list(p.required_skills),
                preferred_skills=list(p.preferred_skills),
            )
            for p in profiles
        ]


def analysis_to_public(analysis: AtsAnalysis) -> AtsAnalysisPublic:
    return _analysis_to_public(analysis)


def history_item_from_row(analysis: AtsAnalysis, resume_title: str | None) -> AtsHistoryItem:
    return AtsHistoryItem(
        id=str(analysis.id),
        resume_id=str(analysis.resume_id),
        resume_title=resume_title,
        ats_score=analysis.ats_score,
        completeness_score=analysis.completeness_score,
        created_at=analysis.created_at,
    )
