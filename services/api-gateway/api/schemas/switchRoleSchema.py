from pydantic import BaseModel


class SwitchRoleRequest(BaseModel):
    """Request body for POST /me/switch-role. Only candidate and recruiter allowed."""
    role: str  # Validated in router: "candidate" | "recruiter"
