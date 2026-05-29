from __future__ import annotations

from pydantic import BaseModel


class AdminStatus(BaseModel):
    ok: bool = True

