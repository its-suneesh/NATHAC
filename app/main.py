from fastapi import FastAPI

from app.api.analyze import router as analyze_router
from app.api.auth import router as auth_router

app = FastAPI(title="NATHAC API")

app.include_router(auth_router)
app.include_router(analyze_router)
