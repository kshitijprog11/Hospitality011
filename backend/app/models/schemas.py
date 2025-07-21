from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    positive = "positive"
    negative = "negative" 
    neutral = "neutral"

class FeedbackStatus(str, Enum):
    new = "new"
    reviewed = "reviewed"
    resolved = "resolved"
    escalated = "escalated"

class FeedbackPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

class FeedbackChannel(str, Enum):
    web = "web"
    email = "email"
    whatsapp = "whatsapp"
    google_reviews = "google_reviews"
    tripadvisor = "tripadvisor"
    booking_com = "booking_com"
    direct = "direct"

# Request Schemas
class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Feedback text content")
    channel: FeedbackChannel = Field(..., description="Source channel of the feedback")
    page: Optional[str] = Field(None, max_length=200, description="Page/service the feedback relates to")
    guest_name: Optional[str] = Field(None, max_length=100, description="Guest first name only")
    guest_contact: Optional[str] = Field(None, max_length=200, description="Guest contact information")
    booking_reference: Optional[str] = Field(None, max_length=100, description="Booking reference number")
    location: Optional[str] = Field(None, max_length=100, description="Hotel/restaurant location")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Feedback text cannot be empty')
        return v.strip()

class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    priority: Optional[FeedbackPriority] = None
    flagged: Optional[bool] = None

# Response Schemas
class FeedbackResponse(BaseModel):
    id: int
    text: str
    channel: str
    page: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    sentiment: Optional[float]
    sentiment_label: Optional[str]
    confidence: Optional[float]
    topics: Optional[List[str]]
    flagged: bool
    status: str
    priority: str
    guest_name: Optional[str]
    booking_reference: Optional[str]
    location: Optional[str]
    processed: bool
    
    class Config:
        from_attributes = True

class FeedbackList(BaseModel):
    items: List[FeedbackResponse]
    total: int
    page: int
    size: int
    pages: int

# Filter Schema
class FeedbackFilter(BaseModel):
    channel: Optional[FeedbackChannel] = None
    status: Optional[FeedbackStatus] = None
    priority: Optional[FeedbackPriority] = None
    sentiment_label: Optional[SentimentLabel] = None
    flagged: Optional[bool] = None
    location: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Text search
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

# Analytics Schemas
class SentimentDistribution(BaseModel):
    positive: int
    negative: int
    neutral: int
    total: int

class TopicAnalysis(BaseModel):
    topic: str
    count: int
    sentiment_avg: float

class AnalyticsResponse(BaseModel):
    sentiment_distribution: SentimentDistribution
    top_topics: List[TopicAnalysis]
    flagged_count: int
    total_feedback: int
    average_sentiment: float
    period_start: datetime
    period_end: datetime

# Alert Schemas
class Alert(BaseModel):
    id: int
    feedback_id: int
    title: str
    message: str
    severity: str  # "low", "medium", "high", "critical"
    created_at: datetime
    resolved: bool = False
    
class AlertCreate(BaseModel):
    feedback_id: int
    title: str
    message: str
    severity: str = "medium"