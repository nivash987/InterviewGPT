from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.job_application import (
    ApplicationStatusHistory,
    InterviewNote,
    JobApplication,
    Reminder,
)
from app.modules.jobs.schemas import (
    InterviewNotePublic,
    JobApplicationDetail,
    JobApplicationPublic,
    ReminderPublic,
    StatusHistoryPublic,
)


class JobsRepository(ABC):
    @abstractmethod
    async def create_application(
        self,
        *,
        user_id: str,
        company_name: str,
        role_title: str,
        status: str,
        location: str | None,
        job_url: str | None,
        salary_range: str | None,
        description: str | None,
        applied_at: datetime | None,
    ) -> JobApplication: ...

    @abstractmethod
    async def get_application_for_user(self, *, application_id: str, user_id: str) -> JobApplication | None: ...

    @abstractmethod
    async def get_application_detail_for_user(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> JobApplication | None: ...

    @abstractmethod
    async def list_applications_for_user(self, *, user_id: str) -> list[JobApplication]: ...

    @abstractmethod
    async def update_application(self, *, application: JobApplication) -> JobApplication: ...

    @abstractmethod
    async def delete_application(self, *, application: JobApplication) -> None: ...

    @abstractmethod
    async def append_status_history(
        self,
        *,
        application_id: str,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> ApplicationStatusHistory: ...

    @abstractmethod
    async def create_note(
        self,
        *,
        application_id: str,
        title: str,
        content: str,
    ) -> InterviewNote: ...

    @abstractmethod
    async def get_note_for_application(
        self,
        *,
        note_id: str,
        application_id: str,
    ) -> InterviewNote | None: ...

    @abstractmethod
    async def update_note(self, *, note: InterviewNote) -> InterviewNote: ...

    @abstractmethod
    async def delete_note(self, *, note: InterviewNote) -> None: ...

    @abstractmethod
    async def create_reminder(
        self,
        *,
        application_id: str,
        title: str,
        remind_at: datetime,
    ) -> Reminder: ...

    @abstractmethod
    async def get_reminder_for_application(
        self,
        *,
        reminder_id: str,
        application_id: str,
    ) -> Reminder | None: ...

    @abstractmethod
    async def update_reminder(self, *, reminder: Reminder) -> Reminder: ...

    @abstractmethod
    async def delete_reminder(self, *, reminder: Reminder) -> None: ...

    @abstractmethod
    async def count_by_status_for_user(self, *, user_id: str) -> dict[str, int]: ...


def _status_history_to_public(entry: ApplicationStatusHistory) -> StatusHistoryPublic:
    return StatusHistoryPublic(
        id=str(entry.id),
        from_status=entry.from_status,
        to_status=entry.to_status,
        note=entry.note,
        created_at=entry.created_at,
    )


def _note_to_public(note: InterviewNote) -> InterviewNotePublic:
    return InterviewNotePublic(
        id=str(note.id),
        application_id=str(note.application_id),
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _reminder_to_public(reminder: Reminder) -> ReminderPublic:
    return ReminderPublic(
        id=str(reminder.id),
        application_id=str(reminder.application_id),
        title=reminder.title,
        remind_at=reminder.remind_at,
        is_completed=reminder.is_completed,
        created_at=reminder.created_at,
    )


def application_to_public(application: JobApplication) -> JobApplicationPublic:
    return JobApplicationPublic(
        id=str(application.id),
        company_name=application.company_name,
        role_title=application.role_title,
        status=application.status,
        location=application.location,
        job_url=application.job_url,
        salary_range=application.salary_range,
        description=application.description,
        applied_at=application.applied_at,
        created_at=application.created_at,
        updated_at=application.updated_at,
    )


def application_to_detail(application: JobApplication) -> JobApplicationDetail:
    base = application_to_public(application)
    return JobApplicationDetail(
        **base.model_dump(),
        status_history=[_status_history_to_public(h) for h in application.status_history],
        interview_notes=[_note_to_public(n) for n in application.interview_notes],
        reminders=[_reminder_to_public(r) for r in application.reminders],
    )


class SqlAlchemyJobsRepository(JobsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_application(
        self,
        *,
        user_id: str,
        company_name: str,
        role_title: str,
        status: str,
        location: str | None,
        job_url: str | None,
        salary_range: str | None,
        description: str | None,
        applied_at: datetime | None,
    ) -> JobApplication:
        application = JobApplication(
            user_id=uuid.UUID(user_id),
            company_name=company_name,
            role_title=role_title,
            status=status,
            location=location,
            job_url=job_url,
            salary_range=salary_range,
            description=description,
            applied_at=applied_at,
        )
        self._session.add(application)
        await self._session.flush()
        history = ApplicationStatusHistory(
            application_id=application.id,
            from_status=None,
            to_status=status,
            note="Application created",
        )
        self._session.add(history)
        await self._session.flush()
        await self._session.refresh(application)
        return application

    async def get_application_for_user(self, *, application_id: str, user_id: str) -> JobApplication | None:
        stmt = select(JobApplication).where(
            JobApplication.id == uuid.UUID(application_id),
            JobApplication.user_id == uuid.UUID(user_id),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_application_detail_for_user(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> JobApplication | None:
        stmt = (
            select(JobApplication)
            .where(
                JobApplication.id == uuid.UUID(application_id),
                JobApplication.user_id == uuid.UUID(user_id),
            )
            .options(
                selectinload(JobApplication.status_history),
                selectinload(JobApplication.interview_notes),
                selectinload(JobApplication.reminders),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_applications_for_user(self, *, user_id: str) -> list[JobApplication]:
        stmt = (
            select(JobApplication)
            .where(JobApplication.user_id == uuid.UUID(user_id))
            .order_by(JobApplication.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_application(self, *, application: JobApplication) -> JobApplication:
        await self._session.flush()
        await self._session.refresh(application)
        return application

    async def delete_application(self, *, application: JobApplication) -> None:
        await self._session.delete(application)
        await self._session.flush()

    async def append_status_history(
        self,
        *,
        application_id: str,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> ApplicationStatusHistory:
        entry = ApplicationStatusHistory(
            application_id=uuid.UUID(application_id),
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def create_note(
        self,
        *,
        application_id: str,
        title: str,
        content: str,
    ) -> InterviewNote:
        note = InterviewNote(
            application_id=uuid.UUID(application_id),
            title=title,
            content=content,
        )
        self._session.add(note)
        await self._session.flush()
        return note

    async def get_note_for_application(
        self,
        *,
        note_id: str,
        application_id: str,
    ) -> InterviewNote | None:
        stmt = select(InterviewNote).where(
            InterviewNote.id == uuid.UUID(note_id),
            InterviewNote.application_id == uuid.UUID(application_id),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_note(self, *, note: InterviewNote) -> InterviewNote:
        await self._session.flush()
        return note

    async def delete_note(self, *, note: InterviewNote) -> None:
        await self._session.delete(note)
        await self._session.flush()

    async def create_reminder(
        self,
        *,
        application_id: str,
        title: str,
        remind_at: datetime,
    ) -> Reminder:
        reminder = Reminder(
            application_id=uuid.UUID(application_id),
            title=title,
            remind_at=remind_at,
        )
        self._session.add(reminder)
        await self._session.flush()
        return reminder

    async def get_reminder_for_application(
        self,
        *,
        reminder_id: str,
        application_id: str,
    ) -> Reminder | None:
        stmt = select(Reminder).where(
            Reminder.id == uuid.UUID(reminder_id),
            Reminder.application_id == uuid.UUID(application_id),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_reminder(self, *, reminder: Reminder) -> Reminder:
        await self._session.flush()
        return reminder

    async def delete_reminder(self, *, reminder: Reminder) -> None:
        await self._session.delete(reminder)
        await self._session.flush()

    async def count_by_status_for_user(self, *, user_id: str) -> dict[str, int]:
        stmt = (
            select(JobApplication.status, func.count())
            .where(JobApplication.user_id == uuid.UUID(user_id))
            .group_by(JobApplication.status)
        )
        result = await self._session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
