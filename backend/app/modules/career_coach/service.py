from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from app.core.errors import BadRequestError, NotFoundError
from app.modules.career_coach.readiness_engine import ReadinessInputs, compute_readiness, normalize_skill
from app.modules.career_coach.repository import CareerCoachRepository
from app.modules.career_coach.roadmap_builder import build_roadmap_milestones, milestones_to_public
from app.modules.career_coach.schemas import (
    MILESTONE_STATUSES,
    PROFICIENCY_LEVELS,
    CareerCoachDashboard,
    CareerRoadmapPublic,
    LearningRecommendation,
    ProgressEntryPublic,
    ProgressUpdateRequest,
    ReadinessScorePublic,
    SkillGapAnalysis,
    UserGoalCreate,
    UserGoalPublic,
    UserSkillPublic,
    UserSkillUpsert,
    WeaknessItem,
)
from app.modules.career_coach.skill_gap import analyze_skill_gaps


def _goal_to_public(goal) -> UserGoalPublic:
    return UserGoalPublic(
        id=str(goal.id),
        target_role=goal.target_role,
        target_timeline_months=goal.target_timeline_months,
        description=goal.description,
        is_active=goal.is_active,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def _skill_to_public(skill) -> UserSkillPublic:
    return UserSkillPublic(
        id=str(skill.id),
        skill_name=skill.skill_name,
        proficiency_level=skill.proficiency_level,
        source=skill.source,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _roadmap_to_public(roadmap) -> CareerRoadmapPublic:
    milestones = milestones_to_public(roadmap.milestones or [])
    progress_map = {p.milestone_id: p.status for p in (roadmap.progress_entries or [])}
    merged = []
    for m in milestones:
        status = progress_map.get(m.id, m.status)
        merged.append(m.model_copy(update={"status": status}))
    return CareerRoadmapPublic(
        id=str(roadmap.id),
        goal_id=str(roadmap.goal_id) if roadmap.goal_id else None,
        title=roadmap.title,
        target_role=roadmap.target_role,
        milestones=merged,
        status=roadmap.status,
        progress_percent=roadmap.progress_percent,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at,
    )


def _readiness_to_public(score) -> ReadinessScorePublic:
    weak_areas = [WeaknessItem.model_validate(w) for w in (score.weak_areas or [])]
    recommendations = [LearningRecommendation.model_validate(r) for r in (score.recommendations or [])]
    return ReadinessScorePublic(
        id=str(score.id),
        overall_score=score.overall_score,
        category_scores=score.category_scores or {},
        weak_areas=weak_areas,
        missing_skills=score.missing_skills or [],
        recommendations=recommendations,
        computed_at=score.computed_at,
    )


class CareerCoachService(ABC):
    @abstractmethod
    async def set_goal(self, *, user_id: str, payload: UserGoalCreate) -> UserGoalPublic: ...

    @abstractmethod
    async def get_goal(self, *, user_id: str) -> UserGoalPublic | None: ...

    @abstractmethod
    async def upsert_skill(self, *, user_id: str, payload: UserSkillUpsert) -> UserSkillPublic: ...

    @abstractmethod
    async def list_skills(self, *, user_id: str) -> list[UserSkillPublic]: ...

    @abstractmethod
    async def sync_skills_from_ats(self, *, user_id: str) -> list[UserSkillPublic]: ...

    @abstractmethod
    async def generate_roadmap(self, *, user_id: str) -> CareerRoadmapPublic: ...

    @abstractmethod
    async def get_roadmap(self, *, user_id: str) -> CareerRoadmapPublic: ...

    @abstractmethod
    async def get_skill_gaps(self, *, user_id: str) -> SkillGapAnalysis: ...

    @abstractmethod
    async def compute_readiness(self, *, user_id: str) -> ReadinessScorePublic: ...

    @abstractmethod
    async def get_readiness(self, *, user_id: str) -> ReadinessScorePublic: ...

    @abstractmethod
    async def update_progress(
        self,
        *,
        user_id: str,
        milestone_id: str,
        payload: ProgressUpdateRequest,
    ) -> ProgressEntryPublic: ...

    @abstractmethod
    async def get_dashboard(self, *, user_id: str) -> CareerCoachDashboard: ...

    @abstractmethod
    async def get_recommendations(self, *, user_id: str) -> list[LearningRecommendation]: ...

    @abstractmethod
    async def get_weaknesses(self, *, user_id: str) -> list[WeaknessItem]: ...


class CareerCoachServiceImpl(CareerCoachService):
    def __init__(self, repository: CareerCoachRepository) -> None:
        self._repo = repository

    async def _resolve_target_role(self, user_id: str) -> str:
        goal = await self._repo.get_active_goal(user_id=user_id)
        if goal:
            return goal.target_role
        roadmap = await self._repo.get_active_roadmap(user_id=user_id)
        if roadmap:
            return roadmap.target_role
        return "Software Engineer"

    async def _user_skill_names(self, user_id: str) -> list[str]:
        skills = await self._repo.list_user_skills(user_id=user_id)
        return [normalize_skill(s.skill_name) for s in skills]

    async def set_goal(self, *, user_id: str, payload: UserGoalCreate) -> UserGoalPublic:
        await self._repo.deactivate_user_goals(user_id=user_id)
        goal = await self._repo.create_goal(
            user_id=user_id,
            target_role=payload.target_role.strip(),
            target_timeline_months=payload.target_timeline_months,
            description=payload.description,
        )
        return _goal_to_public(goal)

    async def get_goal(self, *, user_id: str) -> UserGoalPublic | None:
        goal = await self._repo.get_active_goal(user_id=user_id)
        return _goal_to_public(goal) if goal else None

    async def upsert_skill(self, *, user_id: str, payload: UserSkillUpsert) -> UserSkillPublic:
        if payload.proficiency_level not in PROFICIENCY_LEVELS:
            raise BadRequestError(f"Invalid proficiency_level. Must be one of: {', '.join(PROFICIENCY_LEVELS)}")
        skill = await self._repo.upsert_skill(
            user_id=user_id,
            skill_name=payload.skill_name,
            proficiency_level=payload.proficiency_level,
            source=payload.source,
        )
        return _skill_to_public(skill)

    async def list_skills(self, *, user_id: str) -> list[UserSkillPublic]:
        skills = await self._repo.list_user_skills(user_id=user_id)
        return [_skill_to_public(s) for s in skills]

    async def sync_skills_from_ats(self, *, user_id: str) -> list[UserSkillPublic]:
        synced = await self._repo.sync_skills_from_ats(user_id=user_id)
        return [_skill_to_public(s) for s in synced]

    async def generate_roadmap(self, *, user_id: str) -> CareerRoadmapPublic:
        goal = await self._repo.get_active_goal(user_id=user_id)
        target_role = goal.target_role if goal else "Software Engineer"
        user_skills = await self._user_skill_names(user_id)
        profile = await self._repo.get_job_profile_for_role(role_name=target_role)
        profile_skills = list(profile.required_skills) if profile else None
        gaps = analyze_skill_gaps(
            target_role=target_role,
            user_skills=user_skills,
            profile_required_skills=profile_skills,
        )
        missing = [g.skill_name for g in gaps.missing_skills]
        milestones = build_roadmap_milestones(target_role, missing)

        await self._repo.archive_active_roadmaps(user_id=user_id)
        roadmap = await self._repo.create_roadmap(
            user_id=user_id,
            goal_id=str(goal.id) if goal else None,
            title=f"Career roadmap: {target_role}",
            target_role=target_role,
            milestones=milestones,
        )
        for m in milestones:
            await self._repo.upsert_progress(
                user_id=user_id,
                roadmap_id=str(roadmap.id),
                milestone_id=m["id"],
                status="pending",
                notes=None,
                completed_at=None,
            )
        refreshed = await self._repo.get_active_roadmap(user_id=user_id)
        return _roadmap_to_public(refreshed or roadmap)

    async def get_roadmap(self, *, user_id: str) -> CareerRoadmapPublic:
        roadmap = await self._repo.get_active_roadmap(user_id=user_id)
        if not roadmap:
            raise NotFoundError("No active career roadmap. Generate one first.")
        return _roadmap_to_public(roadmap)

    async def get_skill_gaps(self, *, user_id: str) -> SkillGapAnalysis:
        target_role = await self._resolve_target_role(user_id)
        user_skills = await self._user_skill_names(user_id)
        profile = await self._repo.get_job_profile_for_role(role_name=target_role)
        profile_skills = list(profile.required_skills) if profile else None
        return analyze_skill_gaps(
            target_role=target_role,
            user_skills=user_skills,
            profile_required_skills=profile_skills,
        )

    async def _build_readiness_inputs(self, user_id: str) -> ReadinessInputs:
        target_role = await self._resolve_target_role(user_id)
        user_skills = await self._user_skill_names(user_id)
        profile = await self._repo.get_job_profile_for_role(role_name=target_role)
        profile_skills = list(profile.required_skills) if profile else None
        from app.modules.career_coach.readiness_engine import get_required_skills_for_role

        required = get_required_skills_for_role(target_role, profile_skills)
        ats = await self._repo.get_latest_ats_analysis(user_id=user_id)
        interview_avg, interview_count = await self._repo.get_interview_stats(user_id=user_id)
        job_advanced, job_total = await self._repo.get_job_stats(user_id=user_id)
        roadmap = await self._repo.get_active_roadmap(user_id=user_id)
        roadmap_progress = roadmap.progress_percent if roadmap else 0
        return ReadinessInputs(
            target_role=target_role,
            user_skills=user_skills,
            required_skills=required,
            ats_score=ats.ats_score if ats else None,
            interview_avg_score=interview_avg,
            interview_count=interview_count,
            job_advanced_count=job_advanced,
            job_total_count=job_total,
            roadmap_progress=roadmap_progress,
        )

    async def compute_readiness(self, *, user_id: str) -> ReadinessScorePublic:
        inputs = await self._build_readiness_inputs(user_id)
        result = compute_readiness(inputs)
        score = await self._repo.save_readiness_score(
            user_id=user_id,
            overall_score=result.overall_score,
            category_scores=result.category_scores,
            weak_areas=[w.model_dump() for w in result.weak_areas],
            missing_skills=result.missing_skills,
            recommendations=[r.model_dump() for r in result.recommendations],
        )
        return _readiness_to_public(score)

    async def get_readiness(self, *, user_id: str) -> ReadinessScorePublic:
        score = await self._repo.get_latest_readiness(user_id=user_id)
        if not score:
            return await self.compute_readiness(user_id=user_id)
        return _readiness_to_public(score)

    async def _recalculate_roadmap_progress(self, roadmap) -> None:
        milestones = roadmap.milestones or []
        if not milestones:
            roadmap.progress_percent = 0
            return
        progress_entries = await self._repo.list_progress_for_roadmap(roadmap_id=str(roadmap.id))
        completed_ids = {p.milestone_id for p in progress_entries if p.status == "completed"}
        completed = sum(1 for m in milestones if m.get("id") in completed_ids)
        roadmap.progress_percent = int(round(completed / len(milestones) * 100))
        for m in milestones:
            mid = m.get("id")
            if mid in completed_ids:
                m["status"] = "completed"
        roadmap.milestones = milestones
        await self._repo.update_roadmap(roadmap=roadmap)

    async def update_progress(
        self,
        *,
        user_id: str,
        milestone_id: str,
        payload: ProgressUpdateRequest,
    ) -> ProgressEntryPublic:
        if payload.status not in MILESTONE_STATUSES:
            raise BadRequestError(f"Invalid status. Must be one of: {', '.join(MILESTONE_STATUSES)}")
        roadmap = await self._repo.get_active_roadmap(user_id=user_id)
        if not roadmap:
            raise NotFoundError("No active career roadmap.")
        milestone_ids = {m.get("id") for m in (roadmap.milestones or [])}
        if milestone_id not in milestone_ids:
            raise NotFoundError(f"Milestone '{milestone_id}' not found on active roadmap.")

        completed_at = datetime.now(UTC) if payload.status == "completed" else None
        entry = await self._repo.upsert_progress(
            user_id=user_id,
            roadmap_id=str(roadmap.id),
            milestone_id=milestone_id,
            status=payload.status,
            notes=payload.notes,
            completed_at=completed_at,
        )
        await self._recalculate_roadmap_progress(roadmap)
        return ProgressEntryPublic(
            id=str(entry.id),
            roadmap_id=str(entry.roadmap_id),
            milestone_id=entry.milestone_id,
            status=entry.status,
            notes=entry.notes,
            completed_at=entry.completed_at,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

    async def get_dashboard(self, *, user_id: str) -> CareerCoachDashboard:
        goal = await self.get_goal(user_id=user_id)
        gaps = await self.get_skill_gaps(user_id=user_id)
        latest = await self._repo.get_latest_readiness(user_id=user_id)
        previous = await self._repo.get_previous_readiness(user_id=user_id)
        roadmap = await self._repo.get_active_roadmap(user_id=user_id)

        trend: str | None = None
        readiness_score: int | None = None
        weak_areas: list[WeaknessItem] = []
        recommendations: list[LearningRecommendation] = []
        missing: list[str] = [g.skill_name for g in gaps.missing_skills]

        if latest:
            readiness_score = latest.overall_score
            weak_areas = [WeaknessItem.model_validate(w) for w in (latest.weak_areas or [])]
            recommendations = [LearningRecommendation.model_validate(r) for r in (latest.recommendations or [])]
            missing = latest.missing_skills or missing
            if previous:
                if latest.overall_score > previous.overall_score:
                    trend = "up"
                elif latest.overall_score < previous.overall_score:
                    trend = "down"
                else:
                    trend = "stable"

        return CareerCoachDashboard(
            readiness_score=readiness_score,
            readiness_trend=trend,
            missing_skills=missing[:10],
            roadmap_progress_percent=roadmap.progress_percent if roadmap else None,
            weak_areas=weak_areas,
            recommendations=recommendations,
            active_goal=goal,
            skill_coverage_percent=gaps.coverage_percent,
        )

    async def get_recommendations(self, *, user_id: str) -> list[LearningRecommendation]:
        readiness = await self.get_readiness(user_id=user_id)
        return readiness.recommendations

    async def get_weaknesses(self, *, user_id: str) -> list[WeaknessItem]:
        readiness = await self.get_readiness(user_id=user_id)
        return readiness.weak_areas
