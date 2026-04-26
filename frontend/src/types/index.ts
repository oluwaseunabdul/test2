export interface ResearchGap {
  id: number;
  title: string;
  description: string;
  gap_type: string;
  citation_count: number;
  recency_score: number;
  feasibility_score: number;
  impact_score: number;
  overall_rank: number;
  source_metadata: Record<string, any>;
  related_topics: string[];
  created_at: string;
  vote_count?: number;
}

export interface TrendDataPoint {
  year: number;
  publications: number;
  citations: number;
}

export interface TrendAnalysis {
  topic: string;
  data_points: TrendDataPoint[];
  emerging_keywords: string[];
  declining_keywords: string[];
}

export interface AnalysisRequest {
  field_of_study: string;
  area_of_interest: string;
  research_type: string;
  year_range_start: number;
  year_range_end: number;
  min_citations: number;
  data_source: string;
  gap_types?: string[];
}

export interface AnalysisResponse {
  gaps: ResearchGap[];
  trends?: TrendAnalysis;
  search_strategies?: Record<string, string>;
  pico_suggestions?: PICOData;
}

export interface PICOData {
  population?: string;
  intervention?: string;
  comparator?: string;
  outcomes?: string;
  research_question?: string;
  inclusion_criteria?: Record<string, any>;
  exclusion_criteria?: Record<string, any>;
  prisma_data?: Record<string, any>;
  prospero_draft?: string;
}

export interface Project {
  id: number;
  title: string;
  description?: string;
  field_of_study?: string;
  research_type?: string;
  year_range_start?: number;
  year_range_end?: number;
  min_citations: number;
  data_source: string;
  owner_id: number;
  is_public: boolean;
  share_token: string;
  created_at: string;
  updated_at?: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export const RESEARCH_FIELDS = [
  "Sports Science",
  "Medicine",
  "Psychology",
  "Engineering",
  "Education",
  "Business",
  "Computer Science",
  "Biology",
  "Chemistry",
  "Physics",
  "Environmental Science",
  "Public Health",
  "Nursing",
  "Pharmacy",
  "Social Sciences"
];

export const RESEARCH_TYPES = [
  "Systematic Review",
  "Meta-Analysis",
  "Scoping Review",
  "Narrative Review",
  "Primary Research"
];

export const GAP_TYPES = [
  "Methodological",
  "Population",
  "Intervention",
  "Outcome",
  "Contextual",
  "Theoretical"
];
