from __future__ import annotations

from fastapi import Depends

from app.modules.admin.service import AdminService


def get_admin_service() -> AdminService:
    raise NotImplementedError("Admin service wiring not implemented yet")


AdminServiceDep = Depends(get_admin_service)

