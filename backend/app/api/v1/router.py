from __future__ import annotations

from fastapi import APIRouter

from app.modules.admin.api import router as admin_router
from app.modules.agents.api import router as agents_router
from app.modules.analytics.api import router as analytics_router
from app.modules.auth.api import router as auth_router
from app.modules.coding.api import router as coding_router
from app.modules.interview.api import router as interview_router
from app.modules.placement.api import router as placement_router
from app.modules.rag.api import router as rag_router
from app.modules.resume.api import router as resume_router
from app.modules.study_plan.api import router as study_plan_router
from app.modules.users.api import router as users_router
from app.modules.vision.api import router as vision_router
from app.modules.voice.api import router as voice_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
api_v1_router.include_router(resume_router, prefix="/resume", tags=["resume"])
api_v1_router.include_router(interview_router, prefix="/interview", tags=["interview"])
api_v1_router.include_router(coding_router, prefix="/coding", tags=["coding"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_v1_router.include_router(rag_router, prefix="/rag", tags=["rag"])
api_v1_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_v1_router.include_router(voice_router, prefix="/voice", tags=["voice"])
api_v1_router.include_router(vision_router, prefix="/vision", tags=["vision"])
api_v1_router.include_router(study_plan_router, prefix="/study-plan", tags=["study_plan"])
api_v1_router.include_router(placement_router, prefix="/placement", tags=["placement"])
api_v1_router.include_router(admin_router, prefix="/admin", tags=["admin"])

