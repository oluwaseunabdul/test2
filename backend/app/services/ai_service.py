"""AI/LLM integration for gap analysis and prompt generation.
Supports both FREE local processing and optional LLM enhancement."""
from typing import List, Dict, Any, Optional
import re
from app.core.config import settings


class AIService:
    """Service for AI-powered analysis with FREE local mode + optional LLM enhancement."""
    
    # Gap categories for classification
    GAP_CATEGORIES = {
        "Methodological": [
            "methodological", "study design", "measurement", "bias", 
            "sample size", "randomization", "cross-sectional", "longitudinal"
        ],
        "Population": [
            "population", "demographic", "sample", "generalizability", 
            "underrepresented", "diverse", "specific group"
        ],
        "Intervention": [
            "intervention", "treatment", "protocol", "delivery", 
            "dosage", "duration", "implementation", "fidelity"
        ],
        "Outcome": [
            "outcome", "measure", "endpoint", "follow-up", 
            "long-term", "surrogate", "assessment"
        ],
        "Contextual": [
            "contextual", "setting", "cultural", "geographic", 
            "environment", "context"
        ],
        "Theoretical": [
            "theoretical", "framework", "mechanism", "conceptual", 
            "theory", "pathway"
        ]
    }
    
    def __init__(self):
        self.ai_mode = settings.AI_MODE  # "local" or "llm"
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
    
    async def categorize_gap(self, gap_text: str) -> Dict[str, Any]:
        """Categorize a research gap by type using rule-based or LLM approach."""
        
        # Try LLM if available and enabled
        if self.ai_mode == "llm":
            if self.anthropic_api_key:
                return await self._categorize_with_anthropic(gap_text)
            elif self.openai_api_key:
                return await self._categorize_with_openai(gap_text)
        
        # Default: FREE rule-based categorization (works without any API keys)
        return self._categorize_locally(gap_text)
    
    def _categorize_locally(self, gap_text: str) -> Dict[str, Any]:
        """FREE rule-based gap categorization - no API key needed."""
        text_lower = gap_text.lower()
        scores = {}
        
        for category, keywords in self.GAP_CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        if max(scores.values()) == 0:
            return {
                "category": "Uncategorized",
                "confidence": 0.5,
                "reasoning": "No specific category keywords detected."
            }
        
        best_category = max(scores, key=scores.get)
        confidence = min(1.0, scores[best_category] / 3.0)
        
        return {
            "category": best_category,
            "confidence": confidence,
            "reasoning": f"Matched {scores[best_category]} keywords for {best_category} category."
        }
    
    async def _categorize_with_openai(self, gap_text: str) -> Dict[str, Any]:
        """Use OpenAI to categorize gaps (optional enhancement)."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Categorize this research gap into: Methodological, Population, Intervention, Outcome, Contextual, or Theoretical.
Gap: "{gap_text}"
Respond in JSON: {{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return {"category": "Methodological", "confidence": 0.8, "reasoning": content}
            
        except Exception as e:
            print(f"OpenAI error (falling back to local): {e}")
            return self._categorize_locally(gap_text)
    
    async def _categorize_with_anthropic(self, gap_text: str) -> Dict[str, Any]:
        """Use Anthropic Claude to categorize gaps (optional enhancement)."""
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.anthropic_api_key)
            
            prompt = f"""Categorize this research gap into: Methodological, Population, Intervention, Outcome, Contextual, or Theoretical.
Gap: "{gap_text}"
Respond in JSON: {{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            return {"category": "Methodological", "confidence": 0.8, "reasoning": content}
            
        except Exception as e:
            print(f"Anthropic error (falling back to local): {e}")
            return self._categorize_locally(gap_text)
    
    async def generate_search_strategy(
        self, field: str, topic: str, database: str = "PubMed"
    ) -> str:
        """Generate database-specific search strings (FREE local generation)."""
        
        # Try LLM if available
        if self.ai_mode == "llm":
            if self.anthropic_api_key:
                result = await self._generate_search_anthropic(field, topic, database)
                if not result.startswith("Error"):
                    return result
            elif self.openai_api_key:
                result = await self._generate_search_openai(field, topic, database)
                if not result.startswith("Error"):
                    return result
        
        # FREE template-based generation (works without API keys)
        return self._generate_search_local(field, topic, database)
    
    def _generate_search_local(self, field: str, topic: str, database: str) -> str:
        """FREE template-based search strategy generation."""
        
        # Extract key terms from topic
        terms = [t.strip() for t in re.split(r'[,;]', topic) if t.strip()]
        if len(terms) < 2:
            terms = topic.split()
        
        # Build search components
        main_terms = terms[:3] if len(terms) >= 3 else terms
        
        if database == "PubMed":
            # PubMed syntax with MeSH and free-text
            search_parts = []
            for term in main_terms:
                search_parts.append(f'("{term}"[MeSH Terms] OR "{term}"[Title/Abstract])')
            
            search_string = " AND ".join(search_parts)
            search_string += " AND (systematic review[Publication Type] OR meta-analysis[Publication Type])"
            
            return f"""PubMed Search Strategy:
{search_string}

Filters:
- Publication Date: Last 5-10 years
- Article Type: Systematic Reviews, Meta-Analyses
- Language: English

Tips:
- Use * for truncation (e.g., exercis* finds exercise, exercises)
- Use [mh] for MeSH headings
- Combine with OR for synonyms"""

        elif database == "Embase":
            search_parts = []
            for term in main_terms:
                search_parts.append(f"('{term}':exp OR '{term}':ti,ab)")
            
            return f"""Embase Search Strategy:
{' AND '.join(search_parts)}
AND ('systematic review'/exp OR 'meta analysis'/exp)"""

        elif database == "Scopus":
            return f"""Scopus Search Strategy:
TITLE-ABS-KEY({" AND ".join(main_terms)})
AND (DOCTYPE('re') OR DOCTYPE('ch'))
AND PUBYEAR > {2020 - 5}"""

        elif database == "Web of Science":
            return f"""Web of Science Search Strategy:
TS=({" AND ".join(main_terms)})
Refined to: Review Articles
Timespan: Last 5 years"""

        else:
            return f"""General Search Strategy for {database}:
Keywords: {" AND ".join(main_terms)}
Filters: Review articles, Last 5 years, Peer-reviewed"""
    
    async def _generate_search_openai(self, field: str, topic: str, database: str) -> str:
        """Use OpenAI for enhanced search strategies."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Generate a comprehensive search strategy for {database}:
Field: {field}
Topic: {topic}

Include keywords, Boolean operators, field tags, and filters."""

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating search strategy: {e}"
    
    async def _generate_search_anthropic(self, field: str, topic: str, database: str) -> str:
        """Use Anthropic for enhanced search strategies."""
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.anthropic_api_key)
            
            prompt = f"""Generate a comprehensive search strategy for {database}:
Field: {field}
Topic: {topic}

Include keywords, Boolean operators, field tags, and filters."""

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating search strategy: {e}"
    
    async def generate_pico_research_question(
        self, population: str, intervention: str, comparator: str, outcomes: str
    ) -> str:
        """Generate a structured research question from PICO elements (FREE)."""
        
        # Always use template (works perfectly without API keys)
        return f"""Research Question:

"In {population}, does {intervention} compared to {comparator} improve/affect {outcomes}?"

Alternative formulations:
1. "What is the effect of {intervention} versus {comparator} on {outcomes} in {population}?"
2. "Does {intervention} lead to better {outcomes} than {comparator} among {population}?"
3. "How does {intervention} compare with {comparator} for improving {outcomes} in {population}?"

PICO Summary:
- Population: {population}
- Intervention: {intervention}
- Comparator: {comparator}
- Outcomes: {outcomes}"""
    
    async def generate_prospero_draft(
        self, title: str, pico_data: Dict[str, str], field: str
    ) -> str:
        """Generate a PROSPERO registration draft (FREE template-based)."""
        
        population = pico_data.get('population', 'Not specified')
        intervention = pico_data.get('intervention', 'Not specified')
        comparator = pico_data.get('comparator', 'Not specified')
        outcomes = pico_data.get('outcomes', 'Not specified')
        
        return f"""PROSPERO Systematic Review Registration Draft

TITLE: {title}

FIELD: {field}

1. REVIEW OBJECTIVES
Primary Objective: To systematically review and synthesize evidence on {intervention} for {population}.
Secondary Objectives:
- To evaluate the effectiveness of {intervention} compared to {comparator}
- To assess the impact on {outcomes}
- To identify gaps in current literature

2. SEARCH STRATEGY
Databases: PubMed, Embase, Cochrane Library, Web of Science
Date Range: Inception to present
Language: English (no restrictions considered)
Search Terms: Keywords related to {population}, {intervention}, and {outcomes}

3. INCLUSION CRITERIA
Study Designs: Randomized controlled trials, quasi-experimental studies, observational studies
Population: {population}
Intervention: {intervention}
Comparator: {comparator}
Outcomes: {outcomes}
Publication Status: Published and unpublished studies

4. EXCLUSION CRITERIA
- Case reports, editorials, commentaries
- Studies not reporting relevant outcomes
- Duplicate publications
- Studies with inadequate methodology

5. DATA EXTRACTION
Data will be extracted using a standardized form including:
- Study characteristics (author, year, country, design)
- Participant details (sample size, demographics)
- Intervention details (type, duration, dosage)
- Outcome measures and results
- Risk of bias assessment

6. RISK OF BIAS ASSESSMENT
Tool: Cochrane Risk of Bias Tool (RoB 2) for RCTs, ROBINS-I for non-randomized studies
Domains: Randomization, deviations, missing data, measurement, selection

7. DATA SYNTHESIS
- Narrative synthesis for all included studies
- Meta-analysis if sufficient homogeneous data available
- Subgroup analysis by population characteristics if data permits
- Sensitivity analysis to assess robustness of findings

8. QUALITY OF EVIDENCE
Assessment: GRADE approach for evaluating certainty of evidence

CONTACT INFORMATION
[Your Name and Institution]
[Email Address]"""


# Singleton instance
ai_service = AIService()
