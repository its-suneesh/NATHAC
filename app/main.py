from fastapi import FastAPI
from app.api.analyze import router as analyze_router

app = FastAPI(
    title="NATHAC",
    description="Networked Academic Thinking & Holistic Analysis Core",
    version="1.0.0"
)

app.include_router(analyze_router)
