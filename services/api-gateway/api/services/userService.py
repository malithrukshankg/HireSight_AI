from api.schemas.userSchema import userCreate
from api.repositories.userRepository import UserRepository

class UserService:
    def __init__(self,repo:UserRepository):
        self.repo = repo

    async def create_user(self,payload:userCreate):
        
        return await self.repo.create(payload)

    async def upsert_user(self, email: str, auth0_sub: str, role: str = "candidate"):
        """Upsert a user by auth0_sub."""
        if not email:
            raise ValueError("Email is required")
        
        if not auth0_sub:
            raise ValueError("auth0_sub is required")
        
        if role not in ["admin", "recruiter", "candidate"]:
            raise ValueError(f"Invalid role: {role}. Must be one of: admin, recruiter, candidate")
        
        return await self.repo.upsert_user(email, auth0_sub, role)