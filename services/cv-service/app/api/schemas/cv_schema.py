from __future__ import annotations

from datetime import datetime
import re
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CVUploadResponse(BaseModel):
    id: uuid.UUID
    s3_key: str
    bucket: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None = None
    created_at: datetime
    extraction_status: str
    extracted_text: str | None = None
    page_count: int | None = None
    extraction_error: str | None = None
    structured_extraction_status: str | None = None
    parsed_profile_json: dict[str, Any] | None = None
    structured_extraction_error: str | None = None


class CVByCandidateResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    s3_key: str
    bucket: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None = None
    created_at: datetime


class CVDetailResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    s3_key: str
    bucket: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None = None
    created_at: datetime
    extraction_status: str | None = None
    extracted_text: str | None = None
    structured_extraction_status: str | None = None
    parsed_profile_json: dict[str, Any] | None = None
    structured_extraction_error: str | None = None


class CVExtractionResponse(BaseModel):
    id: uuid.UUID
    extraction_status: str
    extracted_text: str | None = None
    page_count: int | None = None
    extraction_error: str | None = None


class CVExperienceItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company: str
    title: str
    start_date: str
    end_date: str
    description: str


class CVEducationItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    institution: str
    degree: str
    start_date: str
    end_date: str


class CVStructuredProfile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str
    email: str
    phone: str
    skills: list[str] = Field(default_factory=list)
    experience: list[CVExperienceItem] = Field(default_factory=list)
    education: list[CVEducationItem] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError("Email must be in a valid format")
        return value

    @field_validator("skills", "projects")
    @classmethod
    def clean_string_lists(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item and item.strip()]
        seen: set[str] = set()
        deduped: list[str] = []
        for item in cleaned:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped


class CVStructuredExtractionResponse(BaseModel):
    id: uuid.UUID
    structured_extraction_status: str
    parsed_profile_json: CVStructuredProfile | None = None
    structured_extraction_error: str | None = None


class CvParseMetadata(BaseModel):
    parse_version: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    content_hash: str | None = None
    parsed_at: datetime | None = None


class CVAiContextResponse(BaseModel):
    cv_id: uuid.UUID
    candidate_id: uuid.UUID
    extracted_text: str | None = None
    parsed_profile: dict[str, Any] | None = None
    parse_metadata: CvParseMetadata
