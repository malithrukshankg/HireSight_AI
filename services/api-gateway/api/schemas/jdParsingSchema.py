from pydantic import BaseModel, Field


class JobDescriptionParseRequest(BaseModel):
    description: str = Field(min_length=1)
    title: str | None = None


class JobDescriptionParseResponse(BaseModel):
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
