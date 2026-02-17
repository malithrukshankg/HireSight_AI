from database import DBSession
from fastapi import (
    APIRouter,Depends, HTTPException
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

@userRouter.post("/upsert", response_model=userCreate, status_code=200)
async def upsert_user(
    db: DBSession,
    principal: dict = Depends(get_current_principal)
):
    """
    Upsert user data when a user logs in.
    Extracts email, auth0_sub, and role from Auth0 principal and creates or updates the user.
    """
    email = principal.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Auth0 token")
    
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in Auth0 token")
    
    # Extract role from Auth0 claims if available, otherwise default to "candidate"
    role = principal.get("role") or principal.get("https://hiresight.ai/role") or "candidate"
    
    # Ensure role is one of the valid values
    if role not in ["admin", "recruiter", "candidate"]:
        role = "candidate"
    
    controller = UserController(db)
    return await controller.upsert_user(email, auth0_sub, role)