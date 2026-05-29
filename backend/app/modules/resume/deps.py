from __future__ import annotations

from fastapi import Depends

from app.modules.resume.service import ResumeService


def get_resume_service() -> ResumeService:
    raise NotImplementedError("Resume service wiring not implemented yet")


ResumeServiceDep = Depends(get_resume_service)

