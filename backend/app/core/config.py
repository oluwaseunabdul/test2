"""Application configuration and environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Research Topic Discovery Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys (ALL OPTIONAL - platform works without any paid keys)
    OPENAI_API_KEY: Optional[str] = None  # Only needed if you want GPT-4o enhancements
    ANTHROPIC_API_KEY: Optional[str] = None  # Only needed if you want Claude enhancements
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None  # Optional for higher rate limits
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/research_platform"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Redis Cache (optional)
    REDIS_URL: Optional[str] = None  # Set to "redis://localhost:6379/0" if using Redis
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # API Endpoints (ALL FREE - no API keys required)
    PUBMED_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    SEMANTIC_SCHOLAR_BASE_URL: str = "https://api.semanticscholar.org/graph/v1"
    CROSSREF_BASE_URL: str = "https://api.crossref.org/works"
    OPENALEX_BASE_URL: str = "https://api.openalex.org/works"
    
    # AI Mode: "local" (free, rule-based) or "llm" (requires API keys)
    AI_MODE: str = "local"  # Default to free local processing
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
