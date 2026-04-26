"""Research API services for fetching academic papers."""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings


class PubMedService:
    """Service for interacting with PubMed E-utilities API."""
    
    def __init__(self):
        self.base_url = settings.PUBMED_BASE_URL
    
    async def search_systematic_reviews(
        self,
        query: str,
        year_start: int,
        year_end: int,
        min_citations: int = 0
    ) -> List[Dict[str, Any]]:
        """Search for systematic reviews and meta-analyses."""
        # Build PubMed query with filters
        pubmed_query = f"{query} AND (systematic review[pt] OR meta-analysis[pt] OR \"systematic review\"[tiab] OR \"meta analysis\"[tiab])"
        pubmed_query += f" AND ({year_start}:{year_end}[dp])"
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for PMIDs
                search_response = await client.get(
                    f"{self.base_url}/esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": pubmed_query,
                        "retmax": 100,
                        "retmode": "json"
                    },
                    timeout=30.0
                )
                search_data = search_response.json()
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    return []
                
                # Fetch details for PMIDs
                fetch_response = await client.get(
                    f"{self.base_url}/efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(pmids[:20]),  # Limit to 20 for performance
                        "retmode": "json",
                        "rettype": "abstract"
                    },
                    timeout=30.0
                )
                
                return fetch_response.json().get("result", [])
                
        except Exception as e:
            print(f"PubMed API error: {e}")
            return []
    
    async def extract_gap_statements(self, abstracts: List[Dict]) -> List[Dict[str, Any]]:
        """Extract future research statements from abstracts."""
        gaps = []
        gap_keywords = [
            "future research", "further studies", "more research needed",
            "limitations", "should be investigated", "warrants further investigation",
            "additional research", "needs to be explored", "remains to be determined"
        ]
        
        for abstract in abstracts:
            text = abstract.get("abstracttext", "") or ""
            title = abstract.get("title", "")
            
            # Simple keyword-based extraction (can be enhanced with NLP/LLM)
            for sentence in text.split("."):
                sentence = sentence.strip()
                if any(keyword.lower() in sentence.lower() for keyword in gap_keywords):
                    gaps.append({
                        "title": sentence,
                        "source": title,
                        "pmid": abstract.get("pmid"),
                        "type": "extracted"
                    })
        
        return gaps


class SemanticScholarService:
    """Service for interacting with Semantic Scholar API."""
    
    def __init__(self):
        self.base_url = settings.SEMANTIC_SCHOLAR_BASE_URL
        self.headers = {}
        if settings.SEMANTIC_SCHOLAR_API_KEY:
            self.headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
    
    async def search_papers(
        self,
        query: str,
        year_start: int,
        year_end: int,
        min_citations: int = 0
    ) -> List[Dict[str, Any]]:
        """Search for papers using Semantic Scholar."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/paper/search",
                    headers=self.headers,
                    params={
                        "query": query,
                        "year": f"{year_start}-{year_end}",
                        "limit": 50,
                        "fields": "title,abstract,citationCount,year,venue,authors,tldr",
                        "minCitationCount": min_citations
                    },
                    timeout=30.0
                )
                data = response.json()
                return data.get("data", [])
                
        except Exception as e:
            print(f"Semantic Scholar API error: {e}")
            return []
    
    async def get_trending_topics(self, field: str, years: int = 5) -> List[str]:
        """Get trending topics in a specific field."""
        # This is a simplified implementation
        # In production, you'd analyze citation velocity and keyword frequency
        return []


class CrossrefService:
    """Service for interacting with Crossref API."""
    
    def __init__(self):
        self.base_url = settings.CROSSREF_BASE_URL
    
    async def search_works(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for works using Crossref."""
        try:
            async with httpx.AsyncClient() as client:
                params = {"query": query, "rows": 50}
                if filters:
                    params.update(filters)
                
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                return data.get("message", {}).get("items", [])
                
        except Exception as e:
            print(f"Crossref API error: {e}")
            return []


class OpenAlexService:
    """Service for interacting with OpenAlex API."""
    
    def __init__(self):
        self.base_url = settings.OPENALEX_BASE_URL
    
    async def search_works(
        self,
        query: str,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for works using OpenAlex."""
        try:
            async with httpx.AsyncClient() as client:
                params = {"filter": f"title.search:{query}", "per_page": 50}
                if filter_params:
                    # Convert to OpenAlex filter format
                    filters = ",".join([f"{k}:{v}" for k, v in filter_params.items()])
                    params["filter"] += f",{filters}"
                
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                return data.get("results", [])
                
        except Exception as e:
            print(f"OpenAlex API error: {e}")
            return []
    
    async def get_concept_trends(self, concept_id: str) -> List[Dict[str, Any]]:
        """Get publication trends for a concept."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.openalex.org/concepts/{concept_id}",
                    timeout=30.0
                )
                data = response.json()
                return data.get("counts_by_year", [])
                
        except Exception as e:
            print(f"OpenAlex concept error: {e}")
            return []


# Service factory
def get_research_service(provider: str):
    """Get the appropriate research service based on provider."""
    services = {
        "pubmed": PubMedService(),
        "semantic_scholar": SemanticScholarService(),
        "crossref": CrossrefService(),
        "openalex": OpenAlexService()
    }
    return services.get(provider, PubMedService())
