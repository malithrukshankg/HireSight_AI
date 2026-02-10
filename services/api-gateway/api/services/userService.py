from api.schemas.userSchema import userCreate
from api.repositories.userRepository import UserRepository

class UserService:
    def __init__(self,repo:UserRepository):
        self.repo = repo

    async def create_user(self,payload:userCreate):
        
        return await self.repo.create(payload)