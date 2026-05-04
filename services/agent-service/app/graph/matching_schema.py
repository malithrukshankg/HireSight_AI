from __future__ import annotations

from pydantic import BaseModel, Field


class NormalizedJD(BaseModel):
    """Canonical JD representation used by run_matching_analysis.

    All skill/keyword lists are lowercased for case-insensitive comparison.
    all_skills is the deduplicated union of required_skills + preferred_skills
    + tools_technologies, with required skills appearing first.
    """

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    tools_technologies: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
    all_skills: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    seniority_level: str = ""
    employment_type: str = ""
    experience_requirements: str = ""
    summary: str = ""


class NormalizedCV(BaseModel):
    """Canonical CV representation used by run_matching_analysis.

    Nested experience/education objects are flattened to string lists so the
    matching node can work with a uniform data shape.
    """

    skills: list[str] = Field(default_factory=list)
    experience_titles: list[str] = Field(default_factory=list)
    experience_descriptions: list[str] = Field(default_factory=list)
    education_degrees: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
