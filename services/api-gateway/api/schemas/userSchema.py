from pydantic import BaseModel
from enum import Enum
from typing import Optional

class roleTypes(str,Enum):
    admin = "admin"
    recruiter = "recruiter"
    candidate = "candidate"

class userCreate(BaseModel):
    id: int
    name: Optional[str] = ""
    email: str
    password: Optional[str] =""
    role:roleTypes
