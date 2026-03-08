import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from enum import Enum
from datetime import date, datetime


class ImmigrationTarget(str, Enum):
    EB1A = "eb1a"
    EB1B = "eb1b"
    EB1C = "eb1c"
    NIW = "niw"
    O1 = "o1"


class EvidenceSource(str, Enum):
    CV = "cv"
    SCHOLAR = "scholar"
    GITHUB = "github"
    GMAIL = "gmail"
    LINKEDIN = "linkedin"
    CHATGPT_EXPORT = "chatgpt_export"
    CALENDAR = "calendar"
    MANUAL = "manual"


class ConfidenceLevel(BaseModel):
    data_confidence: int = Field(ge=0, le=100)
    criteria_match: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)
    reasoning: str


class Publication(BaseModel):
    title: str
    venue: str
    year: int
    citation_count: Optional[int] = None
    co_authors: list[str] = []
    doi: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel


class Award(BaseModel):
    name: str
    granting_organization: str
    year: int
    scope: str
    description: Optional[str] = None
    source: EvidenceSource
    confidence: ConfidenceLevel


class JudgingRole(BaseModel):
    role: str
    organization: str
    year: int
    documented: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


class MediaCoverage(BaseModel):
    title: str
    outlet: str
    date: Optional[date] = None
    url: Optional[str] = None
    about_person: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


class LeadershipRole(BaseModel):
    title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    is_distinguished_org: bool
    source: EvidenceSource
    confidence: ConfidenceLevel


class ImmigrationProfile(BaseModel):
    name: str
    current_visa_status: Optional[str] = None
    country_of_birth: Optional[str] = None
    target_pathway: ImmigrationTarget
    target_timeline_years: int = Field(ge=1, le=10)
    current_role: Optional[str] = None
    current_employer: Optional[str] = None
    years_experience: Optional[int] = None
    field_of_expertise: str
    publications: list[Publication] = []
    awards: list[Award] = []
    judging_roles: list[JudgingRole] = []
    media_coverage: list[MediaCoverage] = []
    leadership_roles: list[LeadershipRole] = []
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    i10_index: Optional[int] = None
    github_stars: Optional[int] = None
    github_contributions_last_year: Optional[int] = None
    github_pr_reviews: Optional[int] = None
    notable_repos: list[str] = []
    selective_memberships: list[str] = []
    compensation_percentile: Optional[str] = None
    # EB-1B relevant fields
    teaching_experience_years: Optional[int] = None
    research_experience_years: Optional[int] = None
    has_permanent_job_offer: Optional[bool] = None
    job_offer_type: Optional[str] = None
    # EB-1C relevant fields
    managerial_experience_years: Optional[int] = None
    executive_capacity: Optional[bool] = None
    foreign_employer: Optional[str] = None
    foreign_employer_relationship: Optional[str] = None
    data_sources: list[EvidenceSource] = []


class CriterionScore(BaseModel):
    criterion_number: int
    criterion_name: str
    evidence_found: list[str]
    strength: str
    confidence: ConfidenceLevel
    gaps: list[str]
    priority_actions: list[str]


class CriteriaAssessment(BaseModel):
    pathway: ImmigrationTarget
    criteria_scores: list[CriterionScore]
    criteria_met_count: int
    criteria_close_count: int
    overall_readiness: str
    strongest_criteria: list[int]
    weakest_criteria: list[int]
    recommended_focus: list[int]


class RoadmapAction(BaseModel):
    action: str
    description: str
    target_criterion: list[int]
    quarter: str
    effort_level: str
    impact_level: str
    specific_opportunities: list[str] = []


class QuarterlyMilestone(BaseModel):
    quarter: str
    actions: list[RoadmapAction]
    expected_criteria_improvement: dict[int, str]


class ImmigrationRoadmap(BaseModel):
    profile_id: str
    pathway: ImmigrationTarget
    timeline_years: int
    milestones: list[QuarterlyMilestone]
    narrative_summary: str
    disclaimer: str = "This is not legal advice. Consult a qualified immigration attorney."


class RawSourceData(BaseModel):
    source: EvidenceSource
    raw_text: str
    file_name: Optional[str] = None
    metadata: dict = {}


class RawCareerData(BaseModel):
    sources: list[RawSourceData]
    total_files_processed: int
    extraction_notes: list[str] = []


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    onboarding_completed: bool = False


class ConsentRequest(BaseModel):
    source_type: str
    consent_given: bool
    processing_description: str


class OnboardingRequest(BaseModel):
    role_type: str  # "researcher", "engineer", "executive", "entrepreneur", "other"
    primary_field: str
    years_experience: int
    qualifications: list[str]  # ["publications", "managerial", "multinational", "job_offer", "awards"]
    current_visa: Optional[str] = None


class PathwayRecommendation(BaseModel):
    recommended: str
    match_score: int
    explanation: str


class OnboardingResponse(BaseModel):
    recommended_pathway: str
    recommendations: list[PathwayRecommendation]
    profile_id: str


class PathwayUpdateRequest(BaseModel):
    pathway: ImmigrationTarget


class RateLimitResponse(BaseModel):
    message: str
    retry_after: str
    limit_type: str


class ProfileResponse(BaseModel):
    id: str
    status: str
    profile_data: Optional[ImmigrationProfile] = None
    assessment_data: Optional[CriteriaAssessment] = None
    roadmap_data: Optional[ImmigrationRoadmap] = None
    created_at: datetime
    updated_at: datetime
