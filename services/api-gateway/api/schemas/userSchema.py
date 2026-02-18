from pydantic import BaseModel
from enum import Enum
from typing import Optional
import uuid

class roleTypes(str,Enum):
    admin = "admin"
    recruiter = "recruiter"
    candidate = "candidate"

class userCreate(BaseModel):
    id: uuid.UUID
    name: Optional[str] = ""
    email: str
    auth0_sub: Optional[str] =""
    role:roleTypes
