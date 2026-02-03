from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Prompt Management App"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Database
    # Cloud Run has a read-only filesystem except for /tmp
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        import os
        # If running in Cloud Run, use /tmp for SQLite
        if os.getenv("K_SERVICE") and self.DATABASE_URL.startswith("sqlite:///./"):
             return self.DATABASE_URL.replace("sqlite:///./", "sqlite:////tmp/")
        return self.DATABASE_URL

    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Models
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()
