from database import DBSession
from fastapi import (
    APIRouter,Depends
)
from models import User
from api.controllers.userController import UserController
from api.schemas.userSchema import userCreate
from auth.auth0 import get_current_principal

userRouter = APIRouter(prefix="/user",tags=["users"])

@userRouter.post("",response_model=userCreate,status_code=201)
async def create_user(payload: userCreate,db:DBSession,principal: dict = Depends(get_current_principal)):

    user = userCreate(auth0_sub=principal.get("sub"), name =payload.name, email= principal.get("email"))

    return await UserController(db).create_user(user)