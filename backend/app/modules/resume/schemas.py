from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ParsedProject(BaseModel):
    title: str | None = None
    description: str | None = None


class ParsedExperience(BaseModel):
    title: str | None = None
    description: str | None = None


class ParsedEducation(BaseModel):
    title: str | None = None
    description: str | None = None


class ParsedResumeData(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    projects: list[ParsedProject] = Field(default_factory=list)
    experience: list[ParsedExperience] = Field(default_factory=list)
    education: list[ParsedEducation] = Field(default_factory=list)


class ResumeVersionPublic(BaseModel):
    id: str
    resume_id: str
    version_number: int
    original_filename: str
    mime_type: str
    file_size_bytes: int
    parsed_data: ParsedResumeData | None = None
    created_at: datetime


class ResumePublic(BaseModel):
    id: str
    title: str | None = None
    current_version: ResumeVersionPublic | None = None
    version_count: int = 0
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    items: list[ResumePublic]
    total: int


class ResumeHistoryResponse(BaseModel):
    resume_id: str
    versions: list[ResumeVersionPublic]
