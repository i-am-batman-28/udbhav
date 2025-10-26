"""
Data Models for Peer Review System
Defines the structure for submissions, reviews, and related entities
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


# ============================================================================
# ENUMS - Type Definitions
# ============================================================================

class SubmissionType(str, Enum):
    """Type of submission"""
    CODE = "code"
    WRITEUP = "writeup"
    MIXED = "mixed"  # Both code and documents


class SubmissionStatus(str, Enum):
    """Status of a submission"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class ReviewType(str, Enum):
    """Type of review"""
    AI = "ai"
    PEER = "peer"
    INSTRUCTOR = "instructor"


class ReviewStatus(str, Enum):
    """Status of a review"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class PlagiarismRiskLevel(str, Enum):
    """Plagiarism risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    C = "c"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    OTHER = "other"


# ============================================================================
# FILE MODELS
# ============================================================================

class SubmissionFile(BaseModel):
    """Individual file in a submission"""
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_name: str
    saved_name: str
    file_path: str
    file_size: int  # bytes
    file_type: str  # MIME type
    language: Optional[ProgrammingLanguage] = None
    content_hash: Optional[str] = None  # For deduplication
    uploaded_at: datetime = Field(default_factory=datetime.now)


class ExtractedContent(BaseModel):
    """Extracted text/code content from files"""
    file_id: str
    content: str
    length: int
    language: Optional[ProgrammingLanguage] = None
    extraction_method: str  # "ocr", "direct", "parser"


# ============================================================================
# SUBMISSION MODELS
# ============================================================================

class SubmissionMetadata(BaseModel):
    """Metadata for a submission"""
    title: str
    description: Optional[str] = None
    assignment_id: Optional[str] = None
    course_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    programming_languages: List[ProgrammingLanguage] = Field(default_factory=list)
    total_files: int = 0
    total_size: int = 0  # bytes


class Submission(BaseModel):
    """Main submission model"""
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    student_name: str
    student_email: Optional[str] = None
    
    submission_type: SubmissionType
    status: SubmissionStatus = SubmissionStatus.DRAFT
    
    metadata: SubmissionMetadata
    files: List[SubmissionFile] = Field(default_factory=list)
    extracted_content: List[ExtractedContent] = Field(default_factory=list)
    
    submitted_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Review tracking
    ai_review_id: Optional[str] = None
    peer_review_ids: List[str] = Field(default_factory=list)
    instructor_review_id: Optional[str] = None
    
    # Analysis results
    plagiarism_report_id: Optional[str] = None
    code_analysis_id: Optional[str] = None
    
    # Scores
    ai_score: Optional[float] = None
    peer_score_average: Optional[float] = None
    final_score: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# REVIEW CRITERIA MODELS
# ============================================================================

class CriterionScore(BaseModel):
    """Score for a single evaluation criterion"""
    criterion_name: str
    score: float  # 0-100
    weight: float = 1.0
    comment: Optional[str] = None
    
    @validator('score')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Score must be between 0 and 100')
        return v


class EvaluationCriteria(BaseModel):
    """Complete set of evaluation criteria"""
    # For code submissions
    functionality: Optional[CriterionScore] = None
    code_quality: Optional[CriterionScore] = None
    efficiency: Optional[CriterionScore] = None
    documentation: Optional[CriterionScore] = None
    best_practices: Optional[CriterionScore] = None
    innovation: Optional[CriterionScore] = None
    
    # For writeup submissions
    content_quality: Optional[CriterionScore] = None
    structure: Optional[CriterionScore] = None
    analysis: Optional[CriterionScore] = None
    writing_quality: Optional[CriterionScore] = None
    research: Optional[CriterionScore] = None
    originality: Optional[CriterionScore] = None
    
    # Common
    overall_impression: Optional[CriterionScore] = None


# ============================================================================
# REVIEW MODELS
# ============================================================================

class ReviewFeedback(BaseModel):
    """Detailed feedback for a review"""
    summary: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    detailed_comments: Optional[str] = None


class Review(BaseModel):
    """Review of a submission"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str
    
    reviewer_id: str
    reviewer_name: Optional[str] = None  # Anonymous for peer reviews
    reviewer_type: ReviewType
    
    status: ReviewStatus = ReviewStatus.PENDING
    
    # Evaluation
    criteria_scores: Optional[EvaluationCriteria] = None
    overall_score: Optional[float] = None  # Weighted average
    
    # Feedback
    feedback: Optional[ReviewFeedback] = None
    
    # Timestamps
    assigned_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Metadata
    time_spent_minutes: Optional[int] = None
    confidence_level: Optional[float] = None  # 0-1
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReviewAssignment(BaseModel):
    """Assignment of a reviewer to a submission"""
    assignment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str
    reviewer_id: str
    review_id: Optional[str] = None  # Created when review starts
    
    assigned_at: datetime = Field(default_factory=datetime.now)
    due_date: datetime
    status: ReviewStatus = ReviewStatus.PENDING
    
    is_anonymous: bool = True
    priority: int = 0  # Higher = more urgent


# ============================================================================
# PLAGIARISM MODELS
# ============================================================================

class SimilarityMatch(BaseModel):
    """Match between two submissions"""
    matched_submission_id: str
    matched_student_name: Optional[str] = None
    similarity_percentage: float
    match_type: str  # "exact", "paraphrased", "structural"
    confidence: float
    flagged: bool
    matching_sections: List[Dict[str, Any]] = Field(default_factory=list)


class PlagiarismReport(BaseModel):
    """Plagiarism detection report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str
    
    submission_type: SubmissionType
    originality_score: float  # 0-100, higher is better
    risk_level: PlagiarismRiskLevel
    
    total_matches: int
    similarity_matches: List[SimilarityMatch] = Field(default_factory=list)
    flagged_sections: List[Dict[str, Any]] = Field(default_factory=list)
    
    sources_checked: int
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    recommendations: List[str] = Field(default_factory=list)
    requires_manual_review: bool = False


# ============================================================================
# CODE ANALYSIS MODELS
# ============================================================================

class CodeMetrics(BaseModel):
    """Code quality metrics"""
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    cyclomatic_complexity: int
    maintainability_index: float
    comment_ratio: float
    average_function_length: float
    max_function_length: int
    number_of_functions: int
    number_of_classes: int


class StyleIssue(BaseModel):
    """Code style issue"""
    line_number: int
    severity: str  # "error", "warning", "info"
    category: str
    message: str
    suggestion: Optional[str] = None


class CodeQualityScore(BaseModel):
    """Code quality scores"""
    functionality: float
    readability: float
    maintainability: float
    efficiency: float
    style: float
    overall: float
    grade: str  # A, B, C, D, F


class CodeAnalysisReport(BaseModel):
    """Code analysis report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str
    
    language: ProgrammingLanguage
    metrics: CodeMetrics
    quality_score: CodeQualityScore
    
    style_issues: List[StyleIssue] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    best_practices_violations: List[str] = Field(default_factory=list)
    security_concerns: List[str] = Field(default_factory=list)
    
    ai_feedback: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class StudentAnalytics(BaseModel):
    """Analytics for a student"""
    student_id: str
    student_name: str
    
    total_submissions: int
    average_score: float
    best_score: float
    worst_score: float
    
    submissions_by_type: Dict[str, int] = Field(default_factory=dict)
    average_originality: float
    plagiarism_flags: int
    
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    
    submission_history: List[Dict[str, Any]] = Field(default_factory=list)


class ClassAnalytics(BaseModel):
    """Analytics for a class/course"""
    course_id: str
    course_name: str
    
    total_students: int
    total_submissions: int
    average_class_score: float
    
    score_distribution: Dict[str, int] = Field(default_factory=dict)  # Grade -> count
    top_performers: List[Dict[str, Any]] = Field(default_factory=list)
    
    common_issues: List[str] = Field(default_factory=list)
    plagiarism_rate: float
    
    submission_timeline: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# REQUEST/RESPONSE MODELS (for API)
# ============================================================================

class SubmissionCreateRequest(BaseModel):
    """Request to create a new submission"""
    student_id: str
    student_name: str
    student_email: Optional[str] = None
    submission_type: SubmissionType
    title: str
    description: Optional[str] = None
    assignment_id: Optional[str] = None
    course_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ReviewCreateRequest(BaseModel):
    """Request to create a review"""
    submission_id: str
    reviewer_id: str
    reviewer_type: ReviewType
    due_date: Optional[datetime] = None
    is_anonymous: bool = True


class ReviewUpdateRequest(BaseModel):
    """Request to update a review"""
    criteria_scores: Optional[EvaluationCriteria] = None
    feedback: Optional[ReviewFeedback] = None
    status: Optional[ReviewStatus] = None
    time_spent_minutes: Optional[int] = None


class PlagiarismCheckRequest(BaseModel):
    """Request to check plagiarism"""
    submission_id: str
    check_limit: int = 50
    include_archived: bool = False


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis"""
    submission_id: str
    file_ids: Optional[List[str]] = None  # Specific files, or all if None
    include_ai_feedback: bool = True


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SubmissionResponse(BaseModel):
    """Response with submission details"""
    submission: Submission
    reviews_count: int = 0
    has_plagiarism_report: bool = False
    has_code_analysis: bool = False


class ReviewSummary(BaseModel):
    """Summary of reviews for a submission"""
    submission_id: str
    total_reviews: int
    completed_reviews: int
    pending_reviews: int
    average_score: Optional[float] = None
    reviews: List[Review] = Field(default_factory=list)


class DashboardSummary(BaseModel):
    """Dashboard summary for a student"""
    student_id: str
    student_name: str
    
    total_submissions: int
    submissions_under_review: int
    submissions_completed: int
    
    pending_peer_reviews: int  # Reviews student needs to complete
    average_score: Optional[float] = None
    
    recent_submissions: List[Submission] = Field(default_factory=list)
    recent_reviews_received: List[Review] = Field(default_factory=list)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_weighted_score(criteria: EvaluationCriteria) -> float:
    """Calculate weighted overall score from criteria"""
    scores = []
    weights = []
    
    for field_name, field_value in criteria.dict(exclude_none=True).items():
        if isinstance(field_value, dict) and 'score' in field_value:
            scores.append(field_value['score'])
            weights.append(field_value.get('weight', 1.0))
    
    if not scores:
        return 0.0
    
    weighted_sum = sum(s * w for s, w in zip(scores, weights))
    total_weight = sum(weights)
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def determine_grade(score: float) -> str:
    """Convert numerical score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


if __name__ == "__main__":
    # Test models
    print("🧪 Testing Data Models...\n")
    
    # Create a sample submission
    submission = Submission(
        student_id="student-001",
        student_name="John Doe",
        student_email="john@example.com",
        submission_type=SubmissionType.CODE,
        metadata=SubmissionMetadata(
            title="Binary Search Implementation",
            description="Implementing binary search in Python",
            tags=["algorithm", "search", "python"],
            programming_languages=[ProgrammingLanguage.PYTHON]
        )
    )
    
    print("✅ Created submission:")
    print(f"   ID: {submission.submission_id}")
    print(f"   Student: {submission.student_name}")
    print(f"   Type: {submission.submission_type}")
    print(f"   Status: {submission.status}")
    
    # Create a review
    review = Review(
        submission_id=submission.submission_id,
        reviewer_id="reviewer-001",
        reviewer_type=ReviewType.AI,
        overall_score=85.5
    )
    
    print(f"\n✅ Created review:")
    print(f"   ID: {review.review_id}")
    print(f"   Type: {review.reviewer_type}")
    print(f"   Score: {review.overall_score}")
    
    # Test JSON serialization
    submission_json = submission.model_dump_json(indent=2)
    print(f"\n✅ JSON serialization works")
    
    print("\n✅ All data model tests passed!")
