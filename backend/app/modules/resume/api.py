from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse, EmptyData
from app.core.security import Principal
from app.modules.resume.deps import ResumeServiceDep
from app.modules.resume.schemas import ResumeHistoryResponse, ResumeListResponse, ResumePublic
from app.modules.resume.service import ResumeService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())


@router.post("/upload", response_model=ApiResponse[ResumePublic], status_code=201)
async def upload_resume(
    principal: Principal = PrincipalDep,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[ResumePublic]:
    content = await file.read()
    result = await svc.upload_resume(
        user_id=principal.user_id,
        filename=file.filename or "resume.pdf",
        content_type=file.content_type,
        content=content,
        title=title,
    )
    return ApiResponse(data=result)


@router.get("", response_model=ApiResponse[ResumeListResponse])
async def list_resumes(
    principal: Principal = PrincipalDep,
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[ResumeListResponse]:
    result = await svc.list_resumes(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/{resume_id}", response_model=ApiResponse[ResumePublic])
async def get_resume(
    resume_id: str,
    principal: Principal = PrincipalDep,
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[ResumePublic]:
    result = await svc.get_resume(user_id=principal.user_id, resume_id=resume_id)
    return ApiResponse(data=result)


@router.get("/{resume_id}/history", response_model=ApiResponse[ResumeHistoryResponse])
async def get_resume_history(
    resume_id: str,
    principal: Principal = PrincipalDep,
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[ResumeHistoryResponse]:
    result = await svc.get_history(user_id=principal.user_id, resume_id=resume_id)
    return ApiResponse(data=result)


@router.put("/{resume_id}/replace", response_model=ApiResponse[ResumePublic])
async def replace_resume(
    resume_id: str,
    principal: Principal = PrincipalDep,
    file: UploadFile = File(...),
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[ResumePublic]:
    content = await file.read()
    result = await svc.replace_resume(
        user_id=principal.user_id,
        resume_id=resume_id,
        filename=file.filename or "resume.pdf",
        content_type=file.content_type,
        content=content,
    )
    return ApiResponse(data=result)


@router.delete("/{resume_id}", response_model=ApiResponse[EmptyData])
async def delete_resume(
    resume_id: str,
    principal: Principal = PrincipalDep,
    svc: ResumeService = ResumeServiceDep,
) -> ApiResponse[EmptyData]:
    await svc.delete_resume(user_id=principal.user_id, resume_id=resume_id)
    return ApiResponse(data=EmptyData())
