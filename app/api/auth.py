from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# -----------------------------
# Request schema
# -----------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


# -----------------------------
# Login endpoint
# -----------------------------
@router.post("/login")
def login(request: LoginRequest):

    # 🔐 SIMPLE DEMO AUTH (replace later with DB)
    if request.username != "admin" or request.password != "admin123":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": request.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
