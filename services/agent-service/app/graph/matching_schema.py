from __future__ import annotations

import uuid

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


class MatchingInput(BaseModel):
    """All data required by run_matching_analysis to produce a score."""

    job_id: uuid.UUID
    cv_id: uuid.UUID
    request_id: str
    jd: NormalizedJD
    cv: NormalizedCV


class MatchingOutput(BaseModel):
    """Scoring result produced by run_matching_analysis.

    Scores are in [0.0, 1.0].

    required_skills_coverage  -- fraction of JD required_skills matched by CV skills.
    preferred_skills_coverage -- fraction of JD preferred_skills matched by CV skills.
    overall_skills_coverage   -- fraction of JD all_skills matched by CV skills.
    overall                   -- weighted aggregate; the primary sort key for ranking.

    Weights (v1):
        required_skills_coverage  * 0.6
        preferred_skills_coverage * 0.25
        overall_skills_coverage   * 0.15
    """

    required_skills_coverage: float = 0.0
    preferred_skills_coverage: float = 0.0
    overall_skills_coverage: float = 0.0
    overall: float = 0.0
    matched_required: list[str] = Field(default_factory=list)
    matched_preferred: list[str] = Field(default_factory=list)
    unmatched_required: list[str] = Field(default_factory=list)
