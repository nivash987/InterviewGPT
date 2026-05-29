from __future__ import annotations

from fastapi import Depends

from app.modules.voice.service import VoiceService


def get_voice_service() -> VoiceService:
    raise NotImplementedError("Voice service wiring not implemented yet")


VoiceServiceDep = Depends(get_voice_service)

