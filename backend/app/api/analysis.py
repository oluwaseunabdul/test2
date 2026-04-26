"""API routes for research analysis and gap discovery."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from app.db.session import get_db
from app.models import Project, ResearchGap, PICOData
from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ResearchGapResponse,
    ProjectCreate,
    ProjectResponse,
    TrendAnalysis,
    TrendDataPoint
)
from app.services.research_api import PubMedService, SemanticScholarService
from app.services.ai_service import ai_service
from app.nlp.gap_extraction import gap_extractor, trend_analyzer
from app.api.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/analysis", tags=["Research Analysis"])


@router.post("/discover", response_model=AnalysisResponse)
async def discover_gaps(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Discover research gaps based on input parameters."""
    
    # Build search query
    query = f"{request.field_of_study} {request.area_of_interest}"
    
    # Fetch papers from selected data source
    if request.data_source == "live":
        # Use real APIs
        pubmed_service = PubMedService()
        semantic_service = SemanticScholarService()
        
        # Parallel API calls
        pubmed_results, semantic_results = await asyncio.gather(
            pubmed_service.search_systematic_reviews(
                query=query,
                year_start=request.year_range_start,
                year_end=request.year_range_end,
                min_citations=request.min_citations
            ),
            semantic_service.search_papers(
                query=query,
                year_start=request.year_range_start,
                year_end=request.year_range_end,
                min_citations=request.min_citations
            )
        )
        
        # Extract abstracts for gap extraction
        abstracts = []
        citation_counts = []
        
        for paper in semantic_results:
            if paper.get("abstract"):
                abstracts.append(paper["abstract"])
                citation_counts.append(paper.get("citationCount", 0))
        
        for paper in pubmed_results:
            if paper.get("abstracttext"):
                abstracts.append(paper["abstracttext"])
                citation_counts.append(0)  # PubMed doesn't provide citation count directly
        
    else:
        # Mock data for demonstration
        abstracts, citation_counts = _get_mock_abstracts(request)
    
    # Extract gaps using NLP
    extracted_gaps = gap_extractor.extract_gap_statements(abstracts)
    
    # Calculate recency scores
    year_range = request.year_range_end - request.year_range_start
    recency_scores = [
        1.0 - ((request.year_range_end - 2023) / year_range) if year_range > 0 else 0.5
        for _ in extracted_gaps
    ]
    
    # Rank gaps
    ranked_gaps = gap_extractor.rank_gaps(
        extracted_gaps,
        citation_counts=citation_counts[:len(extracted_gaps)],
        recency_scores=recency_scores
    )
    
    # Enhance with AI categorization (optional, can be slow)
    # In production, run this asynchronously or cache results
    enhanced_gaps = []
    for gap in ranked_gaps[:20]:  # Limit to top 20
        enhanced_gaps.append({
            "title": gap["statement"],
            "description": gap["statement"],
            "gap_type": gap["category"],
            "citation_count": 0,
            "recency_score": gap.get("citation_score", 0.5),
            "feasibility_score": gap.get("feasibility_score", 0.6),
            "impact_score": gap.get("impact_score", 0.5),
            "overall_rank": gap.get("overall_rank", 0.5),
            "source_metadata": {},
            "related_topics": []
        })
    
    # Generate trend analysis
    trends = _generate_mock_trends(request)
    
    # Generate search strategies
    search_strategies = {}
    for database in ["PubMed", "Embase", "Scopus"]:
        strategy = await ai_service.generate_search_strategy(
            field=request.field_of_study,
            topic=request.area_of_interest,
            database=database
        )
        search_strategies[database] = strategy
    
    # Generate PICO suggestions
    pico_suggestions = _generate_pico_suggestions(request)
    
    return AnalysisResponse(
        gaps=[ResearchGapResponse(**g) for g in enhanced_gaps],
        trends=trends,
        search_strategies=search_strategies,
        pico_suggestions=pico_suggestions
    )


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new research project."""
    import secrets
    
    db_project = Project(
        **project.dict(),
        owner_id=current_user.id,
        share_token=secrets.token_urlsafe(32)
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's projects."""
    projects = db.query(Project).filter(
        Project.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


def _get_mock_abstracts(request: AnalysisRequest) -> tuple:
    """Generate mock abstracts for demonstration."""
    mock_abstracts = [
        f"Recent studies in {request.field_of_study} have shown promising results. "
        f"However, future research is needed to explore the long-term effects. "
        f"Limitations include small sample sizes and lack of diversity.",
        
        f"This systematic review examined interventions in {request.area_of_interest}. "
        f"Further studies should investigate different populations and settings. "
        f"More rigorous methodology is warranted.",
        
        f"Our meta-analysis reveals significant gaps in current evidence. "
        f"Additional research needs to address methodological limitations. "
        f"The generalizability to other contexts remains unclear.",
        
        f"While our findings are encouraging, more research is needed on optimal dosing. "
        f"Future investigations should use randomized controlled designs. "
        f"Long-term follow-up studies are warranted.",
        
        f"This scoping review identified key areas requiring further exploration. "
        f"Theoretical frameworks need development. "
        f"Cultural factors should be investigated in diverse populations."
    ]
    
    citation_counts = [45, 32, 28, 19, 15]
    
    return mock_abstracts, citation_counts


def _generate_mock_trends(request: AnalysisRequest) -> TrendAnalysis:
    """Generate mock trend data."""
    years = list(range(request.year_range_start, request.year_range_end + 1))
    
    data_points = [
        TrendDataPoint(
            year=year,
            publications=50 + (year - request.year_range_start) * 10,
            citations=200 + (year - request.year_range_start) * 30
        )
        for year in years
    ]
    
    return TrendAnalysis(
        topic=request.area_of_interest,
        data_points=data_points,
        emerging_keywords=["AI applications", "personalized approaches", "digital health"],
        declining_keywords=["traditional methods", "manual assessment"]
    )


def _generate_pico_suggestions(request: AnalysisRequest) -> dict:
    """Generate PICO suggestions based on the research area."""
    return {
        "population": f"Adults with conditions related to {request.field_of_study}",
        "intervention": "Evidence-based interventions specific to the research question",
        "comparator": "Standard care or alternative interventions",
        "outcomes": "Clinical outcomes, quality of life, cost-effectiveness",
        "research_question": None,
        "inclusion_criteria": {
            "study_types": ["RCTs", "Observational studies", "Systematic reviews"],
            "language": "English",
            "publication_date": f"{request.year_range_start}-{request.year_range_end}"
        },
        "exclusion_criteria": {
            "study_types": ["Case reports", "Editorials", "Commentaries"],
            "population": "Animal studies, pediatric populations (unless relevant)"
        }
    }
