from __future__ import annotations

from pydantic import BaseModel


class KnowledgeDocumentPublic(BaseModel):
    content_item_id: str
    title: str | None = None

