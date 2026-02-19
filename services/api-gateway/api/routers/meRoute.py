"""
Routes for the currently authenticated user (e.g. /me/...).
"""
from fastapi import APIRouter, Depends, HTTPException
from auth.auth0 import get_current_principal
from auth.auth0_management import (
    assign_role_to_user,
    get_role_id,
    SELF_ASSIGNABLE_ROLES,
)
from api.schemas.switchRoleSchema import SwitchRoleRequest

meRouter = APIRouter(prefix="/me", tags=["me"])


@meRouter.post("/switch-role", status_code=200)
async def switch_role(
    payload: SwitchRoleRequest,
    principal: dict = Depends(get_current_principal),
):
    """
    Allow authenticated users to switch between candidate and recruiter roles.
    Admin is NOT self-assignable. Role change is persisted in Auth0 via Management API.
    User must re-login or refresh token to receive a new JWT with the updated role.
    """
    role = payload.role.strip().lower() if payload.role else ""
    if role not in SELF_ASSIGNABLE_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: '{payload.role}'. Only 'candidate' and 'recruiter' are allowed.",
        )

    user_id = principal.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID (sub) not found in token")

    try:
        get_role_id(role)  # validates env vars
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        await assign_role_to_user(user_id, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Role updated successfully. Please refresh or re-login to receive a new token with the updated role.",
        "role": role,
    }
