from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.ats import AtsAnalysis, JobProfile
from app.db.models.career_coach import CareerRoadmap, ProgressTracking, ReadinessScore, UserGoal, UserSkill
from app.db.models.interview import InterviewSession
from app.db.models.job_application import JobApplication


class CareerCoachRepository(ABC):
    @abstractmethod
    async def create_goal(
        self,
        *,
        user_id: str,
        target_role: str,
        target_timeline_months: int | None,
        description: str | None,
    ) -> UserGoal: ...

    @abstractmethod
    async def deactivate_user_goals(self, *, user_id: str) -> None: ...

    @abstractmethod
    async def get_active_goal(self, *, user_id: str) -> UserGoal | None: ...

    @abstractmethod
    async def upsert_skill(
        self,
        *,
        user_id: str,
        skill_name: str,
        proficiency_level: str,
        source: str,
    ) -> UserSkill: ...

    @abstractmethod
    async def list_user_skills(self, *, user_id: str) -> list[UserSkill]: ...

    @abstractmethod
    async def create_roadmap(
        self,
        *,
        user_id: str,
        goal_id: str | None,
        title: str,
        target_role: str,
        milestones: list,
    ) -> CareerRoadmap: ...

    @abstractmethod
    async def archive_active_roadmaps(self, *, user_id: str) -> None: ...

    @abstractmethod
    async def get_active_roadmap(self, *, user_id: str) -> CareerRoadmap | None: ...

    @abstractmethod
    async def update_roadmap(self, *, roadmap: CareerRoadmap) -> CareerRoadmap: ...

    @abstractmethod
    async def upsert_progress(
        self,
        *,
        user_id: str,
        roadmap_id: str,
        milestone_id: str,
        status: str,
        notes: str | None,
        completed_at: datetime | None,
    ) -> ProgressTracking: ...

    @abstractmethod
    async def list_progress_for_roadmap(self, *, roadmap_id: str) -> list[ProgressTracking]: ...

    @abstractmethod
    async def save_readiness_score(
        self,
        *,
        user_id: str,
        overall_score: int,
        category_scores: dict,
        weak_areas: list,
        missing_skills: list,
        recommendations: list,
    ) -> ReadinessScore: ...

    @abstractmethod
    async def get_latest_readiness(self, *, user_id: str) -> ReadinessScore | None: ...

    @abstractmethod
    async def get_previous_readiness(self, *, user_id: str) -> ReadinessScore | None: ...

    @abstractmethod
    async def get_latest_ats_analysis(self, *, user_id: str) -> AtsAnalysis | None: ...

    @abstractmethod
    async def get_job_profile_for_role(self, *, role_name: str) -> JobProfile | None: ...

    @abstractmethod
    async def get_interview_stats(self, *, user_id: str) -> tuple[float | None, int]: ...

    @abstractmethod
    async def get_job_stats(self, *, user_id: str) -> tuple[int, int]: ...

    @abstractmethod
    async def sync_skills_from_ats(self, *, user_id: str) -> list[UserSkill]: ...


class SqlAlchemyCareerCoachRepository(CareerCoachRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_goal(
        self,
        *,
        user_id: str,
        target_role: str,
        target_timeline_months: int | None,
        description: str | None,
    ) -> UserGoal:
        goal = UserGoal(
            user_id=uuid.UUID(user_id),
            target_role=target_role,
            target_timeline_months=target_timeline_months,
            description=description,
            is_active=True,
        )
        self._session.add(goal)
        await self._session.flush()
        return goal

    async def deactivate_user_goals(self, *, user_id: str) -> None:
        result = await self._session.execute(
            select(UserGoal).where(
                UserGoal.user_id == uuid.UUID(user_id),
                UserGoal.is_active.is_(True),
            ),
        )
        for goal in result.scalars().all():
            goal.is_active = False
        await self._session.flush()

    async def get_active_goal(self, *, user_id: str) -> UserGoal | None:
        result = await self._session.execute(
            select(UserGoal)
            .where(UserGoal.user_id == uuid.UUID(user_id), UserGoal.is_active.is_(True))
            .order_by(desc(UserGoal.created_at))
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def upsert_skill(
        self,
        *,
        user_id: str,
        skill_name: str,
        proficiency_level: str,
        source: str,
    ) -> UserSkill:
        normalized = skill_name.strip().lower()
        result = await self._session.execute(
            select(UserSkill).where(
                UserSkill.user_id == uuid.UUID(user_id),
                func.lower(UserSkill.skill_name) == normalized,
            ),
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.proficiency_level = proficiency_level
            existing.source = source
            existing.skill_name = skill_name.strip()
            await self._session.flush()
            return existing

        skill = UserSkill(
            user_id=uuid.UUID(user_id),
            skill_name=skill_name.strip(),
            proficiency_level=proficiency_level,
            source=source,
        )
        self._session.add(skill)
        await self._session.flush()
        return skill

    async def list_user_skills(self, *, user_id: str) -> list[UserSkill]:
        result = await self._session.execute(
            select(UserSkill)
            .where(UserSkill.user_id == uuid.UUID(user_id))
            .order_by(UserSkill.skill_name),
        )
        return list(result.scalars().all())

    async def create_roadmap(
        self,
        *,
        user_id: str,
        goal_id: str | None,
        title: str,
        target_role: str,
        milestones: list,
    ) -> CareerRoadmap:
        roadmap = CareerRoadmap(
            user_id=uuid.UUID(user_id),
            goal_id=uuid.UUID(goal_id) if goal_id else None,
            title=title,
            target_role=target_role,
            milestones=milestones,
            status="active",
            progress_percent=0,
        )
        self._session.add(roadmap)
        await self._session.flush()
        return roadmap

    async def archive_active_roadmaps(self, *, user_id: str) -> None:
        result = await self._session.execute(
            select(CareerRoadmap).where(
                CareerRoadmap.user_id == uuid.UUID(user_id),
                CareerRoadmap.status == "active",
            ),
        )
        for roadmap in result.scalars().all():
            roadmap.status = "archived"
        await self._session.flush()

    async def get_active_roadmap(self, *, user_id: str) -> CareerRoadmap | None:
        result = await self._session.execute(
            select(CareerRoadmap)
            .options(selectinload(CareerRoadmap.progress_entries))
            .where(CareerRoadmap.user_id == uuid.UUID(user_id), CareerRoadmap.status == "active")
            .order_by(desc(CareerRoadmap.created_at))
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def update_roadmap(self, *, roadmap: CareerRoadmap) -> CareerRoadmap:
        await self._session.flush()
        return roadmap

    async def upsert_progress(
        self,
        *,
        user_id: str,
        roadmap_id: str,
        milestone_id: str,
        status: str,
        notes: str | None,
        completed_at: datetime | None,
    ) -> ProgressTracking:
        result = await self._session.execute(
            select(ProgressTracking).where(
                ProgressTracking.roadmap_id == uuid.UUID(roadmap_id),
                ProgressTracking.milestone_id == milestone_id,
            ),
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.status = status
            existing.notes = notes
            existing.completed_at = completed_at
            await self._session.flush()
            return existing

        entry = ProgressTracking(
            user_id=uuid.UUID(user_id),
            roadmap_id=uuid.UUID(roadmap_id),
            milestone_id=milestone_id,
            status=status,
            notes=notes,
            completed_at=completed_at,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def list_progress_for_roadmap(self, *, roadmap_id: str) -> list[ProgressTracking]:
        result = await self._session.execute(
            select(ProgressTracking).where(ProgressTracking.roadmap_id == uuid.UUID(roadmap_id)),
        )
        return list(result.scalars().all())

    async def save_readiness_score(
        self,
        *,
        user_id: str,
        overall_score: int,
        category_scores: dict,
        weak_areas: list,
        missing_skills: list,
        recommendations: list,
    ) -> ReadinessScore:
        score = ReadinessScore(
            user_id=uuid.UUID(user_id),
            overall_score=overall_score,
            category_scores=category_scores,
            weak_areas=weak_areas,
            missing_skills=missing_skills,
            recommendations=recommendations,
            computed_at=datetime.now(UTC),
        )
        self._session.add(score)
        await self._session.flush()
        return score

    async def get_latest_readiness(self, *, user_id: str) -> ReadinessScore | None:
        result = await self._session.execute(
            select(ReadinessScore)
            .where(ReadinessScore.user_id == uuid.UUID(user_id))
            .order_by(desc(ReadinessScore.computed_at))
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def get_previous_readiness(self, *, user_id: str) -> ReadinessScore | None:
        result = await self._session.execute(
            select(ReadinessScore)
            .where(ReadinessScore.user_id == uuid.UUID(user_id))
            .order_by(desc(ReadinessScore.computed_at))
            .offset(1)
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def get_latest_ats_analysis(self, *, user_id: str) -> AtsAnalysis | None:
        result = await self._session.execute(
            select(AtsAnalysis)
            .where(AtsAnalysis.user_id == uuid.UUID(user_id))
            .order_by(desc(AtsAnalysis.created_at))
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def get_job_profile_for_role(self, *, role_name: str) -> JobProfile | None:
        result = await self._session.execute(
            select(JobProfile).where(func.lower(JobProfile.role_name) == role_name.strip().lower()),
        )
        return result.scalar_one_or_none()

    async def get_interview_stats(self, *, user_id: str) -> tuple[float | None, int]:
        result = await self._session.execute(
            select(InterviewSession).where(
                InterviewSession.user_id == uuid.UUID(user_id),
                InterviewSession.status == "completed",
                InterviewSession.total_score.is_not(None),
            ),
        )
        sessions = list(result.scalars().all())
        if not sessions:
            return None, 0
        avg = sum(s.total_score or 0 for s in sessions) / len(sessions)
        return avg, len(sessions)

    async def get_job_stats(self, *, user_id: str) -> tuple[int, int]:
        result = await self._session.execute(
            select(JobApplication).where(JobApplication.user_id == uuid.UUID(user_id)),
        )
        apps = list(result.scalars().all())
        advanced_statuses = {"interview_scheduled", "interview_completed", "offer"}
        advanced = sum(1 for a in apps if a.status in advanced_statuses)
        return advanced, len(apps)

    async def sync_skills_from_ats(self, *, user_id: str) -> list[UserSkill]:
        ats = await self.get_latest_ats_analysis(user_id=user_id)
        if not ats:
            return []
        synced: list[UserSkill] = []
        for skill in ats.skills_found or []:
            if isinstance(skill, str) and skill.strip():
                synced.append(
                    await self.upsert_skill(
                        user_id=user_id,
                        skill_name=skill,
                        proficiency_level="intermediate",
                        source="ats",
                    ),
                )
        return synced
