from __future__ import annotations

from fastapi import Depends

from app.modules.analytics.service import AnalyticsService


def get_analytics_service() -> AnalyticsService:
    raise NotImplementedError("Analytics service wiring not implemented yet")


AnalyticsServiceDep = Depends(get_analytics_service)

