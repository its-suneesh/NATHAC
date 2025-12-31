from fastapi import APIRouter, HTTPException
from app.models.auth import LoginRequest
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(request: LoginRequest):
    """
    Authenticates a user and returns a JWT token.
    Fixed security vulnerability where token was generated after failure.
    """
    
    if request.username == settings.USERNAME and request.password == settings.PASSWORD:
        access_token = create_access_token(
            data={"sub": request.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")