from database import DBSession
from fastapi import (
    APIRouter,
    HTTPException,
    status
)
from models import User
from api.controllers.userController import UserController
from api.schemas.userSchema import userCreate

userRouter = APIRouter(prefix="/user",tags=["users"])

@userRouter.post("",response_model=userCreate,status_code=201)
async def create_user(payload: userCreate,db:DBSession):
    return await UserController(db).create_user(payload)