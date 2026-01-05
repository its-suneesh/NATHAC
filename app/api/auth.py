from fastapi import APIRouter, HTTPException
import secrets
from app.models.auth import LoginRequest
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(request: LoginRequest):
    """
    Authenticates a user securely.
    """
    
    is_username_correct = secrets.compare_digest(request.username, settings.USERNAME)
    is_password_correct = secrets.compare_digest(request.password, settings.PASSWORD)

    if is_username_correct and is_password_correct:
        access_token = create_access_token(
            data={"sub": request.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")