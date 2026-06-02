from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.errors import BadRequestError, NotFoundError
from app.modules.jobs.repository import (
    JobsRepository,
    _note_to_public,
    _reminder_to_public,
    _status_history_to_public,
    application_to_detail,
    application_to_public,
)
from app.modules.jobs.schemas import (
    APPLICATION_STATUSES,
    InterviewNoteCreate,
    InterviewNotePublic,
    InterviewNoteUpdate,
    JobApplicationCreate,
    JobApplicationDetail,
    JobApplicationListResponse,
    JobApplicationPublic,
    JobApplicationUpdate,
    JobsAnalyticsSummary,
    ReminderCreate,
    ReminderPublic,
    ReminderUpdate,
    StatusUpdateRequest,
    TimelineResponse,
)


class JobsService(ABC):
    @abstractmethod
    async def create_application(self, *, user_id: str, payload: JobApplicationCreate) -> JobApplicationPublic: ...

    @abstractmethod
    async def list_applications(self, *, user_id: str) -> JobApplicationListResponse: ...

    @abstractmethod
    async def get_application(self, *, user_id: str, application_id: str) -> JobApplicationDetail: ...

    @abstractmethod
    async def update_application(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: JobApplicationUpdate,
    ) -> JobApplicationPublic: ...

    @abstractmethod
    async def delete_application(self, *, user_id: str, application_id: str) -> None: ...

    @abstractmethod
    async def update_status(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: StatusUpdateRequest,
    ) -> JobApplicationPublic: ...

    @abstractmethod
    async def get_timeline(self, *, user_id: str, application_id: str) -> TimelineResponse: ...

    @abstractmethod
    async def add_note(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: InterviewNoteCreate,
    ) -> InterviewNotePublic: ...

    @abstractmethod
    async def update_note(
        self,
        *,
        user_id: str,
        application_id: str,
        note_id: str,
        payload: InterviewNoteUpdate,
    ) -> InterviewNotePublic: ...

    @abstractmethod
    async def delete_note(self, *, user_id: str, application_id: str, note_id: str) -> None: ...

    @abstractmethod
    async def add_reminder(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: ReminderCreate,
    ) -> ReminderPublic: ...

    @abstractmethod
    async def update_reminder(
        self,
        *,
        user_id: str,
        application_id: str,
        reminder_id: str,
        payload: ReminderUpdate,
    ) -> ReminderPublic: ...

    @abstractmethod
    async def delete_reminder(self, *, user_id: str, application_id: str, reminder_id: str) -> None: ...

    @abstractmethod
    async def get_analytics(self, *, user_id: str) -> JobsAnalyticsSummary: ...


class JobsServiceImpl(JobsService):
    def __init__(self, *, repository: JobsRepository) -> None:
        self._repository = repository

    def _validate_status(self, status: str) -> None:
        if status not in APPLICATION_STATUSES:
            raise BadRequestError(f"Invalid status. Must be one of: {', '.join(APPLICATION_STATUSES)}")

    async def _get_owned_application(self, *, user_id: str, application_id: str):
        application = await self._repository.get_application_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Job application not found")
        return application

    async def create_application(self, *, user_id: str, payload: JobApplicationCreate) -> JobApplicationPublic:
        self._validate_status(payload.status)
        application = await self._repository.create_application(
            user_id=user_id,
            company_name=payload.company_name,
            role_title=payload.role_title,
            status=payload.status,
            location=payload.location,
            job_url=payload.job_url,
            salary_range=payload.salary_range,
            description=payload.description,
            applied_at=payload.applied_at,
        )
        return application_to_public(application)

    async def list_applications(self, *, user_id: str) -> JobApplicationListResponse:
        applications = await self._repository.list_applications_for_user(user_id=user_id)
        return JobApplicationListResponse(items=[application_to_public(a) for a in applications])

    async def get_application(self, *, user_id: str, application_id: str) -> JobApplicationDetail:
        application = await self._repository.get_application_detail_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Job application not found")
        return application_to_detail(application)

    async def update_application(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: JobApplicationUpdate,
    ) -> JobApplicationPublic:
        application = await self._get_owned_application(user_id=user_id, application_id=application_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return application_to_public(application)
        for key, value in updates.items():
            setattr(application, key, value)
        updated = await self._repository.update_application(application=application)
        return application_to_public(updated)

    async def delete_application(self, *, user_id: str, application_id: str) -> None:
        application = await self._get_owned_application(user_id=user_id, application_id=application_id)
        await self._repository.delete_application(application=application)

    async def update_status(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: StatusUpdateRequest,
    ) -> JobApplicationPublic:
        self._validate_status(payload.status)
        application = await self._get_owned_application(user_id=user_id, application_id=application_id)
        from_status = application.status
        if from_status == payload.status:
            return application_to_public(application)
        application.status = payload.status
        await self._repository.append_status_history(
            application_id=application_id,
            from_status=from_status,
            to_status=payload.status,
            note=payload.note,
        )
        updated = await self._repository.update_application(application=application)
        return application_to_public(updated)

    async def get_timeline(self, *, user_id: str, application_id: str) -> TimelineResponse:
        application = await self._repository.get_application_detail_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Job application not found")
        events = [_status_history_to_public(h) for h in application.status_history]
        return TimelineResponse(application_id=application_id, events=events)

    async def add_note(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: InterviewNoteCreate,
    ) -> InterviewNotePublic:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        note = await self._repository.create_note(
            application_id=application_id,
            title=payload.title,
            content=payload.content,
        )
        return _note_to_public(note)

    async def update_note(
        self,
        *,
        user_id: str,
        application_id: str,
        note_id: str,
        payload: InterviewNoteUpdate,
    ) -> InterviewNotePublic:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        note = await self._repository.get_note_for_application(note_id=note_id, application_id=application_id)
        if note is None:
            raise NotFoundError("Note not found")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(note, key, value)
        updated_note = await self._repository.update_note(note=note)
        return _note_to_public(updated_note)

    async def delete_note(self, *, user_id: str, application_id: str, note_id: str) -> None:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        note = await self._repository.get_note_for_application(note_id=note_id, application_id=application_id)
        if note is None:
            raise NotFoundError("Note not found")
        await self._repository.delete_note(note=note)

    async def add_reminder(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: ReminderCreate,
    ) -> ReminderPublic:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        reminder = await self._repository.create_reminder(
            application_id=application_id,
            title=payload.title,
            remind_at=payload.remind_at,
        )
        return _reminder_to_public(reminder)

    async def update_reminder(
        self,
        *,
        user_id: str,
        application_id: str,
        reminder_id: str,
        payload: ReminderUpdate,
    ) -> ReminderPublic:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        reminder = await self._repository.get_reminder_for_application(
            reminder_id=reminder_id,
            application_id=application_id,
        )
        if reminder is None:
            raise NotFoundError("Reminder not found")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(reminder, key, value)
        updated_reminder = await self._repository.update_reminder(reminder=reminder)
        return _reminder_to_public(updated_reminder)

    async def delete_reminder(self, *, user_id: str, application_id: str, reminder_id: str) -> None:
        await self._get_owned_application(user_id=user_id, application_id=application_id)
        reminder = await self._repository.get_reminder_for_application(
            reminder_id=reminder_id,
            application_id=application_id,
        )
        if reminder is None:
            raise NotFoundError("Reminder not found")
        await self._repository.delete_reminder(reminder=reminder)

    async def get_analytics(self, *, user_id: str) -> JobsAnalyticsSummary:
        by_status = await self._repository.count_by_status_for_user(user_id=user_id)
        total = sum(by_status.values())
        interviews_scheduled = by_status.get("interview_scheduled", 0) + by_status.get("interview_completed", 0)
        offers = by_status.get("offer", 0)
        rejections = by_status.get("rejected", 0)
        terminal = offers + rejections + by_status.get("withdrawn", 0)
        success_rate = round((offers / terminal) * 100, 1) if terminal > 0 else 0.0
        return JobsAnalyticsSummary(
            total_applications=total,
            interviews_scheduled=interviews_scheduled,
            offers_received=offers,
            rejections=rejections,
            success_rate=success_rate,
            by_status=by_status,
        )
