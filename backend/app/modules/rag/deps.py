from __future__ import annotations

from fastapi import Depends

from app.modules.rag.service import RagService


def get_rag_service() -> RagService:
    raise NotImplementedError("RAG service wiring not implemented yet")


RagServiceDep = Depends(get_rag_service)

