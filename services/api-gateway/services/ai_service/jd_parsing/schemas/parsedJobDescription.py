from pydantic import BaseModel, Field


class ParsedJobDescription(BaseModel):
    summary: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    experience_requirements: str = ""
    seniority_level: str = ""
    employment_type: str = ""
    tools_technologies: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
