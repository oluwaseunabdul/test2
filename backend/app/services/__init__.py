"""Services module initialization."""
from app.services.research_api import (
    PubMedService,
    SemanticScholarService,
    CrossrefService,
    OpenAlexService,
    get_research_service
)
from app.services.ai_service import AIService, ai_service

__all__ = [
    "PubMedService",
    "SemanticScholarService",
    "CrossrefService",
    "OpenAlexService",
    "get_research_service",
    "AIService",
    "ai_service"
]
