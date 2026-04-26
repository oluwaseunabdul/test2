"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    field_of_study: Optional[str] = None
    research_type: Optional[str] = None
    year_range_start: Optional[int] = None
    year_range_end: Optional[int] = None
    min_citations: int = 0
    data_source: str = "mock"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    field_of_study: Optional[str] = None
    research_type: Optional[str] = None
    year_range_start: Optional[int] = None
    year_range_end: Optional[int] = None
    min_citations: Optional[int] = None
    data_source: Optional[str] = None
    is_public: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    is_public: bool
    share_token: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Research Gap Schemas
class ResearchGapBase(BaseModel):
    title: str
    description: Optional[str] = None
    gap_type: Optional[str] = None
    citation_count: int = 0
    recency_score: Optional[float] = None
    feasibility_score: Optional[float] = None
    impact_score: Optional[float] = None
    overall_rank: Optional[float] = None
    source_metadata: Optional[Dict[str, Any]] = None
    related_topics: Optional[List[str]] = None


class ResearchGapCreate(ResearchGapBase):
    project_id: int


class ResearchGapResponse(ResearchGapBase):
    id: int
    project_id: int
    created_at: datetime
    vote_count: int = 0
    
    class Config:
        from_attributes = True


# PICO Schema
class PICODataBase(BaseModel):
    population: Optional[str] = None
    intervention: Optional[str] = None
    comparator: Optional[str] = None
    outcomes: Optional[str] = None
    research_question: Optional[str] = None
    inclusion_criteria: Optional[Dict[str, Any]] = None
    exclusion_criteria: Optional[Dict[str, Any]] = None
    prisma_data: Optional[Dict[str, Any]] = None
    prospero_draft: Optional[str] = None


class PICODataCreate(PICODataBase):
    project_id: int


class PICODataResponse(PICODataBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Comment Schema
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    project_id: Optional[int] = None
    gap_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    project_id: Optional[int] = None
    gap_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analysis Request/Response
class AnalysisRequest(BaseModel):
    field_of_study: str
    area_of_interest: str
    research_type: str
    year_range_start: int
    year_range_end: int
    min_citations: int = 0
    data_source: str = "mock"
    gap_types: Optional[List[str]] = None


class TrendDataPoint(BaseModel):
    year: int
    publications: int
    citations: int


class TrendAnalysis(BaseModel):
    topic: str
    data_points: List[TrendDataPoint]
    emerging_keywords: List[str] = []
    declining_keywords: List[str] = []


class AnalysisResponse(BaseModel):
    gaps: List[ResearchGapResponse]
    trends: Optional[TrendAnalysis] = None
    search_strategies: Optional[Dict[str, str]] = None
    pico_suggestions: Optional[PICODataBase] = None


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
