from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

APPLICATION_STATUSES = (
    "applied",
    "screening",
    "interview_scheduled",
    "interview_completed",
    "offer",
    "rejected",
    "withdrawn",
)


class JobApplicationCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=256)
    role_title: str = Field(min_length=1, max_length=256)
    status: str = "applied"
    location: str | None = None
    job_url: str | None = None
    salary_range: str | None = None
    description: str | None = None
    applied_at: datetime | None = None


class JobApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=256)
    role_title: str | None = Field(default=None, min_length=1, max_length=256)
    location: str | None = None
    job_url: str | None = None
    salary_range: str | None = None
    description: str | None = None
    applied_at: datetime | None = None


class StatusUpdateRequest(BaseModel):
    status: str
    note: str | None = None


class InterviewNoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1)


class InterviewNoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=256)
    content: str | None = Field(default=None, min_length=1)


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    remind_at: datetime


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=256)
    remind_at: datetime | None = None
    is_completed: bool | None = None


class StatusHistoryPublic(BaseModel):
    id: str
    from_status: str | None
    to_status: str
    note: str | None
    created_at: datetime


class InterviewNotePublic(BaseModel):
    id: str
    application_id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class ReminderPublic(BaseModel):
    id: str
    application_id: str
    title: str
    remind_at: datetime
    is_completed: bool
    created_at: datetime


class JobApplicationPublic(BaseModel):
    id: str
    company_name: str
    role_title: str
    status: str
    location: str | None
    job_url: str | None
    salary_range: str | None
    description: str | None
    applied_at: datetime | None
    created_at: datetime
    updated_at: datetime


class JobApplicationDetail(JobApplicationPublic):
    status_history: list[StatusHistoryPublic] = Field(default_factory=list)
    interview_notes: list[InterviewNotePublic] = Field(default_factory=list)
    reminders: list[ReminderPublic] = Field(default_factory=list)


class JobApplicationListResponse(BaseModel):
    items: list[JobApplicationPublic]


class JobsAnalyticsSummary(BaseModel):
    total_applications: int
    interviews_scheduled: int
    offers_received: int
    rejections: int
    success_rate: float
    by_status: dict[str, int]


class TimelineResponse(BaseModel):
    application_id: str
    events: list[StatusHistoryPublic]
