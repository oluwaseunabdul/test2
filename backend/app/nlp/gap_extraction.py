"""NLP utilities for text processing and gap extraction."""
import re
from typing import List, Dict, Any, Tuple
from collections import Counter


class GapExtractor:
    """Extract and categorize research gaps from text."""
    
    GAP_CATEGORIES = [
        "Methodological",
        "Population", 
        "Intervention",
        "Outcome",
        "Contextual",
        "Theoretical"
    ]
    
    GAP_PATTERNS = {
        "Methodological": [
            r"methodological\s+limitations?",
            r"study\s+design\s+limitations?",
            r"measurement\s+issues?",
            r"bias\s+concerns?",
            r"small\s+sample\s+size",
            r"lack\s+of\s+randomi?sation",
            r"cross-sectional\s+design"
        ],
        "Population": [
            r"limited\s+(to|population|sample)",
            r"specific\s+(group|demographic|population)",
            r"generalizability\s+(issues|concerns|limitations)",
            r"underrepresented\s+(groups|populations)",
            r"diverse\s+(samples|populations)"
        ],
        "Intervention": [
            r"intervention\s+(details|protocols|delivery)",
            r"treatment\s+(duration|dosage|intensity)",
            r"implementation\s+(strategies|barriers)",
            r"fidelity\s+(issues|concerns)"
        ],
        "Outcome": [
            r"outcome\s+(measures|assessment|selection)",
            r"follow-up\s+(period|duration|time)",
            r"long-term\s+(effects|outcomes|impact)",
            r"surrogate\s+(endpoints|markers|outcomes)"
        ],
        "Contextual": [
            r"contextual\s+(factors|variables)",
            r"setting\s+(specific|differences)",
            r"cultural\s+(factors|considerations|contexts)",
            r"geographic\s+(limitations|variation)"
        ],
        "Theoretical": [
            r"theoretical\s+(framework|basis|foundation)",
            r"mechanism\s+(of\s+action|pathways)",
            r"conceptual\s+(model|framework)",
            r"theory-driven\s+(research|studies)"
        ]
    }
    
    FUTURE_RESEARCH_INDICATORS = [
        "future research",
        "further studies",
        "more research needed",
        "should be investigated",
        "warrants further investigation",
        "additional research",
        "needs to be explored",
        "remains to be determined",
        "unclear whether",
        "evidence is limited",
        "more rigorous studies",
        "larger scale studies",
        "long-term studies"
    ]
    
    def extract_gap_statements(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract potential gap statements from text."""
        gaps = []
        
        for text in texts:
            sentences = self._split_sentences(text)
            
            for sentence in sentences:
                if self._is_gap_statement(sentence):
                    category = self._categorize_gap(sentence)
                    gaps.append({
                        "statement": sentence.strip(),
                        "category": category,
                        "confidence": self._calculate_confidence(sentence, category)
                    })
        
        return gaps
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be enhanced with NLTK/spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _is_gap_statement(self, sentence: str) -> bool:
        """Check if a sentence indicates a research gap."""
        sentence_lower = sentence.lower()
        return any(
            indicator in sentence_lower 
            for indicator in self.FUTURE_RESEARCH_INDICATORS
        )
    
    def _categorize_gap(self, sentence: str) -> str:
        """Categorize a gap statement by type."""
        sentence_lower = sentence.lower()
        scores = {}
        
        for category, patterns in self.GAP_PATTERNS.items():
            score = sum(
                1 for pattern in patterns 
                if re.search(pattern, sentence_lower)
            )
            scores[category] = score
        
        if max(scores.values()) == 0:
            return "Uncategorized"
        
        return max(scores, key=scores.get)
    
    def _calculate_confidence(self, sentence: str, category: str) -> float:
        """Calculate confidence score for categorization."""
        sentence_lower = sentence.lower()
        
        if category == "Uncategorized":
            return 0.5
        
        matching_patterns = sum(
            1 for pattern in self.GAP_PATTERNS.get(category, [])
            if re.search(pattern, sentence_lower)
        )
        
        # Normalize to 0-1 range (assuming max 5 patterns could match)
        return min(1.0, matching_patterns / 3.0)
    
    def rank_gaps(
        self,
        gaps: List[Dict[str, Any]],
        citation_counts: List[int] = None,
        recency_scores: List[float] = None
    ) -> List[Dict[str, Any]]:
        """Rank gaps by impact, feasibility, and recency."""
        
        for i, gap in enumerate(gaps):
            # Calculate component scores
            citation_score = 0.0
            if citation_counts and i < len(citation_counts):
                # Normalize citation count (log scale)
                import math
                citation_score = math.log1p(citation_counts[i]) / 10.0
                citation_score = min(1.0, citation_score)
            
            recency_score = recency_scores[i] if recency_scores and i < len(recency_scores) else 0.5
            
            # Feasibility based on gap type and specificity
            feasibility_score = self._estimate_feasibility(gap["statement"])
            
            # Impact based on category and confidence
            impact_weights = {
                "Methodological": 0.8,
                "Population": 0.7,
                "Intervention": 0.9,
                "Outcome": 0.85,
                "Contextual": 0.6,
                "Theoretical": 0.75,
                "Uncategorized": 0.5
            }
            impact_score = (
                impact_weights.get(gap["category"], 0.5) * 0.6 +
                gap.get("confidence", 0.5) * 0.4
            )
            
            # Overall ranking score
            overall_rank = (
                citation_score * 0.25 +
                recency_score * 0.25 +
                feasibility_score * 0.20 +
                impact_score * 0.30
            )
            
            gap["citation_score"] = citation_score
            gap["feasibility_score"] = feasibility_score
            gap["impact_score"] = impact_score
            gap["overall_rank"] = overall_rank
        
        # Sort by overall rank (descending)
        return sorted(gaps, key=lambda x: x["overall_rank"], reverse=True)
    
    def _estimate_feasibility(self, statement: str) -> float:
        """Estimate feasibility of addressing the gap."""
        statement_lower = statement.lower()
        
        # High feasibility indicators
        high_feasibility = [
            "survey", "questionnaire", "interview",
            "secondary analysis", "systematic review",
            "meta-analysis", "observational"
        ]
        
        # Low feasibility indicators
        low_feasibility = [
            "randomized controlled trial", "longitudinal",
            "decades", "expensive", "costly",
            "large-scale", "multi-center"
        ]
        
        high_score = sum(1 for term in high_feasibility if term in statement_lower)
        low_score = sum(1 for term in low_feasibility if term in statement_lower)
        
        # Base feasibility around 0.6, adjusted by indicators
        base = 0.6
        adjustment = (high_score - low_score) * 0.1
        return max(0.1, min(1.0, base + adjustment))


class TrendAnalyzer:
    """Analyze publication trends and detect emerging topics."""
    
    def __init__(self):
        pass
    
    def analyze_trends(
        self,
        publications_by_year: Dict[int, int],
        citations_by_year: Dict[int, int],
        keywords_by_year: Dict[int, List[str]]
    ) -> Dict[str, Any]:
        """Analyze trends and identify emerging/declining topics."""
        
        years = sorted(publications_by_year.keys())
        
        # Calculate growth rates
        pub_growth = self._calculate_growth_rate(publications_by_year, years)
        citation_growth = self._calculate_growth_rate(citations_by_year, years)
        
        # Analyze keyword trends
        keyword_trends = self._analyze_keyword_trends(keywords_by_year, years)
        
        # Identify emerging and declining keywords
        emerging = [
            kw for kw, trend in keyword_trends.items()
            if trend["growth_rate"] > 0.2 and trend["recent_frequency"] > 2
        ]
        
        declining = [
            kw for kw, trend in keyword_trends.items()
            if trend["growth_rate"] < -0.1
        ]
        
        return {
            "publication_trend": pub_growth,
            "citation_trend": citation_growth,
            "emerging_keywords": emerging[:10],  # Top 10
            "declining_keywords": declining[:10],
            "keyword_trends": keyword_trends
        }
    
    def _calculate_growth_rate(
        self,
        data: Dict[int, int],
        years: List[int]
    ) -> float:
        """Calculate average annual growth rate."""
        if len(years) < 2:
            return 0.0
        
        values = [data.get(y, 0) for y in years]
        
        # Simple linear regression slope
        n = len(years)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_x2 = sum(i ** 2 for i in range(n))
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Convert to percentage growth rate
        avg_value = sum_y / n if n > 0 else 1
        return (slope / avg_value) * 100 if avg_value > 0 else 0.0
    
    def _analyze_keyword_trends(
        self,
        keywords_by_year: Dict[int, List[str]],
        years: List[int]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze frequency trends for each keyword."""
        
        # Count keyword frequencies by year
        keyword_counts = {}
        for year in years:
            keywords = keywords_by_year.get(year, [])
            for kw in keywords:
                if kw not in keyword_counts:
                    keyword_counts[kw] = {}
                keyword_counts[kw][year] = keyword_counts[kw].get(year, 0) + 1
        
        # Calculate trends for each keyword
        trends = {}
        for keyword, year_counts in keyword_counts.items():
            recent_years = [y for y in years if y >= years[-1] - 2]
            early_years = [y for y in years if y <= years[0] + 2]
            
            recent_freq = sum(year_counts.get(y, 0) for y in recent_years)
            early_freq = sum(year_counts.get(y, 0) for y in early_years)
            
            growth_rate = (
                (recent_freq - early_freq) / early_freq
                if early_freq > 0 else 0
            )
            
            trends[keyword] = {
                "total_count": sum(year_counts.values()),
                "recent_frequency": recent_freq,
                "early_frequency": early_freq,
                "growth_rate": growth_rate
            }
        
        return trends


# Singleton instances
gap_extractor = GapExtractor()
trend_analyzer = TrendAnalyzer()
