from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.errors import BadRequestError, NotFoundError
from app.modules.ats.analyzer import analyze_resume
from app.modules.ats.repository import (
    AtsRepository,
    analysis_to_public,
    history_item_from_row,
)
from app.modules.ats.schemas import AtsAnalysisPublic, AtsAnalysisResult, AtsHistoryResponse
from app.modules.resume.parser import parse_resume_text
from app.modules.resume.repository import ResumeRepository
from app.modules.resume.schemas import ParsedResumeData


class AtsService(ABC):
    @abstractmethod
    async def analyze_resume(self, *, user_id: str, resume_id: str) -> AtsAnalysisResult: ...

    @abstractmethod
    async def get_latest_analysis(self, *, user_id: str, resume_id: str) -> AtsAnalysisPublic: ...

    @abstractmethod
    async def get_history(self, *, user_id: str) -> AtsHistoryResponse: ...


class AtsServiceImpl(AtsService):
    def __init__(
        self,
        *,
        ats_repository: AtsRepository,
        resume_repository: ResumeRepository,
    ) -> None:
        self._ats_repository = ats_repository
        self._resume_repository = resume_repository

    async def _load_resume_data(self, *, user_id: str, resume_id: str) -> tuple[ParsedResumeData, str]:
        resume = await self._resume_repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        version = resume.current_version
        if version is None:
            raise BadRequestError("Resume has no uploaded version to analyze")

        raw_text = version.raw_text or ""
        if not raw_text.strip():
            raise BadRequestError("Resume has no extractable text. Upload a PDF or DOCX with readable content.")

        if version.parsed_data:
            parsed = ParsedResumeData.model_validate(version.parsed_data)
        else:
            parsed = parse_resume_text(raw_text)

        return parsed, raw_text

    async def analyze_resume(self, *, user_id: str, resume_id: str) -> AtsAnalysisResult:
        parsed, raw_text = await self._load_resume_data(user_id=user_id, resume_id=resume_id)

        taxonomy_skills = await self._ats_repository.list_taxonomy_skills()
        job_profiles = await self._ats_repository.list_job_profiles()

        result = analyze_resume(
            parsed=parsed,
            raw_text=raw_text,
            taxonomy_skills=taxonomy_skills,
            job_profiles=job_profiles,
        )

        await self._ats_repository.create_analysis(
            user_id=user_id,
            resume_id=resume_id,
            ats_score=result.ats_score,
            completeness_score=result.completeness_score,
            section_scores=result.section_scores.model_dump(),
            skills_found=result.skills_found,
            missing_skills=result.missing_skills,
            keyword_coverage=result.keyword_coverage.model_dump(),
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            suggestions=result.suggestions,
            recommended_roles=[r.model_dump() for r in result.recommended_roles],
        )

        return result

    async def get_latest_analysis(self, *, user_id: str, resume_id: str) -> AtsAnalysisPublic:
        resume = await self._resume_repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        analysis = await self._ats_repository.get_latest_for_resume(user_id=user_id, resume_id=resume_id)
        if analysis is None:
            raise NotFoundError("No ATS analysis found for this resume. Run an analysis first.")

        return analysis_to_public(analysis)

    async def get_history(self, *, user_id: str) -> AtsHistoryResponse:
        rows = await self._ats_repository.list_history_for_user(user_id=user_id)
        items = [history_item_from_row(analysis, title) for analysis, title in rows]
        return AtsHistoryResponse(items=items, total=len(items))
