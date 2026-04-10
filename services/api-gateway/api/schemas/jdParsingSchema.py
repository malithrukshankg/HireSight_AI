from pydantic import BaseModel, Field

from api.schemas.parsedJobDescriptionSchema import ParsedJobDescriptionSchema


class JobDescriptionParseRequest(BaseModel):
    description: str = Field(min_length=1)
    title: str | None = None


class JobDescriptionParseResponse(ParsedJobDescriptionSchema):
    pass
