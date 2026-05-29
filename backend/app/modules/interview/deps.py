from __future__ import annotations

from fastapi import Depends

from app.modules.interview.service import InterviewService


def get_interview_service() -> InterviewService:
    raise NotImplementedError("Interview service wiring not implemented yet")


InterviewServiceDep = Depends(get_interview_service)

