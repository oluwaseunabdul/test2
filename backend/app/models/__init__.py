"""Database models for the research platform."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    """User model for authentication and project ownership."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    """Research project model."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    field_of_study = Column(String(100))
    research_type = Column(String(50))  # SLR, Meta-Analysis, Scoping, Narrative
    year_range_start = Column(Integer)
    year_range_end = Column(Integer)
    min_citations = Column(Integer, default=0)
    data_source = Column(String(50), default="mock")  # mock or live
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    share_token = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="projects")
    gaps = relationship("ResearchGap", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="project", cascade="all, delete-orphan")
    pico_data = relationship("PICOData", back_populates="project", uselist=False, cascade="all, delete-orphan")


class ResearchGap(Base):
    """Identified research gap from analysis."""
    __tablename__ = "research_gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    gap_type = Column(String(50))  # Methodological, Population, Intervention, Outcome, Contextual, Theoretical
    citation_count = Column(Integer, default=0)
    recency_score = Column(Float)
    feasibility_score = Column(Float)
    impact_score = Column(Float)
    overall_rank = Column(Float)
    source_metadata = Column(JSON)
    related_topics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="gaps")
    votes = relationship("GapVote", back_populates="gap", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="gap", cascade="all, delete-orphan")


class GapVote(Base):
    """Votes for prioritizing research gaps."""
    __tablename__ = "gap_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    gap_id = Column(Integer, ForeignKey("research_gaps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    vote_value = Column(Integer)  # +1 for upvote, -1 for downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    gap = relationship("ResearchGap", back_populates="votes")


class Comment(Base):
    """Comments on research gaps or projects."""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    gap_id = Column(Integer, ForeignKey("research_gaps.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="comments")
    gap = relationship("ResearchGap", back_populates="comments")


class PICOData(Base):
    """PICO framework data for a project."""
    __tablename__ = "pico_data"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    population = Column(Text)
    intervention = Column(Text)
    comparator = Column(Text)
    outcomes = Column(Text)
    research_question = Column(Text)
    inclusion_criteria = Column(JSON)
    exclusion_criteria = Column(JSON)
    prisma_data = Column(JSON)
    prospero_draft = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="pico_data")
