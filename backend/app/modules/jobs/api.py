from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse, EmptyData
from app.core.security import Principal
from app.modules.jobs.deps import JobsServiceDep
from app.modules.jobs.schemas import (
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
from app.modules.jobs.service import JobsService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())


@router.get("/analytics/summary", response_model=ApiResponse[JobsAnalyticsSummary])
async def analytics_summary(
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobsAnalyticsSummary]:
    result = await svc.get_analytics(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse[JobApplicationPublic], status_code=201)
async def create_application(
    payload: JobApplicationCreate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobApplicationPublic]:
    result = await svc.create_application(user_id=principal.user_id, payload=payload)
    return ApiResponse(data=result)


@router.get("", response_model=ApiResponse[JobApplicationListResponse])
async def list_applications(
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobApplicationListResponse]:
    result = await svc.list_applications(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/{application_id}", response_model=ApiResponse[JobApplicationDetail])
async def get_application(
    application_id: str,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobApplicationDetail]:
    result = await svc.get_application(user_id=principal.user_id, application_id=application_id)
    return ApiResponse(data=result)


@router.patch("/{application_id}", response_model=ApiResponse[JobApplicationPublic])
async def update_application(
    application_id: str,
    payload: JobApplicationUpdate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobApplicationPublic]:
    result = await svc.update_application(
        user_id=principal.user_id,
        application_id=application_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.delete("/{application_id}", response_model=ApiResponse[EmptyData])
async def delete_application(
    application_id: str,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[EmptyData]:
    await svc.delete_application(user_id=principal.user_id, application_id=application_id)
    return ApiResponse(data=EmptyData())


@router.post("/{application_id}/status", response_model=ApiResponse[JobApplicationPublic])
async def update_status(
    application_id: str,
    payload: StatusUpdateRequest,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[JobApplicationPublic]:
    result = await svc.update_status(
        user_id=principal.user_id,
        application_id=application_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.get("/{application_id}/timeline", response_model=ApiResponse[TimelineResponse])
async def get_timeline(
    application_id: str,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[TimelineResponse]:
    result = await svc.get_timeline(user_id=principal.user_id, application_id=application_id)
    return ApiResponse(data=result)


@router.post("/{application_id}/notes", response_model=ApiResponse[InterviewNotePublic], status_code=201)
async def add_note(
    application_id: str,
    payload: InterviewNoteCreate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[InterviewNotePublic]:
    result = await svc.add_note(
        user_id=principal.user_id,
        application_id=application_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.patch(
    "/{application_id}/notes/{note_id}",
    response_model=ApiResponse[InterviewNotePublic],
)
async def update_note(
    application_id: str,
    note_id: str,
    payload: InterviewNoteUpdate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[InterviewNotePublic]:
    result = await svc.update_note(
        user_id=principal.user_id,
        application_id=application_id,
        note_id=note_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.delete("/{application_id}/notes/{note_id}", response_model=ApiResponse[EmptyData])
async def delete_note(
    application_id: str,
    note_id: str,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[EmptyData]:
    await svc.delete_note(
        user_id=principal.user_id,
        application_id=application_id,
        note_id=note_id,
    )
    return ApiResponse(data=EmptyData())


@router.post("/{application_id}/reminders", response_model=ApiResponse[ReminderPublic], status_code=201)
async def add_reminder(
    application_id: str,
    payload: ReminderCreate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[ReminderPublic]:
    result = await svc.add_reminder(
        user_id=principal.user_id,
        application_id=application_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.patch(
    "/{application_id}/reminders/{reminder_id}",
    response_model=ApiResponse[ReminderPublic],
)
async def update_reminder(
    application_id: str,
    reminder_id: str,
    payload: ReminderUpdate,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[ReminderPublic]:
    result = await svc.update_reminder(
        user_id=principal.user_id,
        application_id=application_id,
        reminder_id=reminder_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.delete("/{application_id}/reminders/{reminder_id}", response_model=ApiResponse[EmptyData])
async def delete_reminder(
    application_id: str,
    reminder_id: str,
    principal: Principal = PrincipalDep,
    svc: JobsService = JobsServiceDep,
) -> ApiResponse[EmptyData]:
    await svc.delete_reminder(
        user_id=principal.user_id,
        application_id=application_id,
        reminder_id=reminder_id,
    )
    return ApiResponse(data=EmptyData())
