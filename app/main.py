from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.v1.api import api_router
from app.api.v1.endpoints import prompts, execute, providers
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("Startup: Initializing application...")
    create_db_and_tables()
    yield
    # Shutdown: Cleanup
    print("Shutdown: Cleaning up...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing and testing LLM prompts",
    version="0.1.0",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(execute.router, prefix="/api/v1/execute", tags=["execute"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Prompt Management API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
