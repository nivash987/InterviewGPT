from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import Settings


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_resume_file(
    *,
    filename: str,
    content_type: str | None,
    size_bytes: int,
    max_size_bytes: int,
) -> str:
    """Return normalized extension (.pdf or .docx). Raises ValueError on invalid input."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported MIME type: {content_type}")

    if size_bytes <= 0:
        raise ValueError("File is empty")

    if size_bytes > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ValueError(f"File exceeds maximum size of {max_mb:.1f} MB")

    return ext


class LocalResumeStorage:
    def __init__(self, settings: Settings) -> None:
        self._base_dir = Path(settings.resume_upload_dir)
        self._max_size = settings.resume_max_file_size_bytes

    @property
    def max_file_size_bytes(self) -> int:
        return self._max_size

    def validate(self, *, filename: str, content_type: str | None, size_bytes: int) -> str:
        return validate_resume_file(
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            max_size_bytes=self._max_size,
        )

    def build_path(self, *, user_id: str, resume_id: str, version_id: str, extension: str) -> Path:
        safe_ext = extension if extension.startswith(".") else f".{extension}"
        directory = self._base_dir / user_id / resume_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{version_id}{safe_ext}"

    def save(self, *, path: Path, content: bytes) -> None:
        path.write_bytes(content)

    def delete_file(self, path: Path) -> None:
        if path.is_file():
            path.unlink()

    def delete_resume_directory(self, *, user_id: str, resume_id: str) -> None:
        directory = self._base_dir / user_id / resume_id
        if directory.is_dir():
            for child in directory.iterdir():
                if child.is_file():
                    child.unlink()
            directory.rmdir()

    @staticmethod
    def new_version_id() -> str:
        return str(uuid.uuid4())
