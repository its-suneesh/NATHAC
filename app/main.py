from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.api.auth import router as auth_router
from app.core.logging_config import app_logger

http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes the shared HTTP client.
    """
    global http_client
    app_logger.info("Starting up: Initializing shared HTTP client...")
    
    http_client = httpx.AsyncClient(timeout=30.0)
    
    app.state.http_client = http_client
    
    
    yield
    
    app_logger.info("Shutting down: Closing shared HTTP client...")
    if http_client:
        await http_client.aclose()

app = FastAPI(title="NATHAC API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(analyze_router)