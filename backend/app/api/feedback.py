from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..models.schemas import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, 
    FeedbackList, FeedbackFilter, AnalyticsResponse,
    FeedbackChannel, FeedbackStatus, FeedbackPriority, SentimentLabel
)
from ..services.feedback_service import feedback_service

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("/", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new feedback entry with automatic NLP analysis
    
    This endpoint:
    - Creates a new feedback record
    - Automatically analyzes sentiment using AI models
    - Extracts topics and keywords
    - Flags urgent issues for immediate attention
    - Returns the processed feedback with analysis results
    """
    try:
        return await feedback_service.create_feedback(db, feedback_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating feedback: {str(e)}")

@router.get("/", response_model=FeedbackList)
async def get_feedback_list(
    # Filtering parameters
    channel: Optional[FeedbackChannel] = Query(None, description="Filter by feedback channel"),
    status: Optional[FeedbackStatus] = Query(None, description="Filter by feedback status"),
    priority: Optional[FeedbackPriority] = Query(None, description="Filter by priority level"),
    sentiment_label: Optional[SentimentLabel] = Query(None, description="Filter by sentiment"),
    flagged: Optional[bool] = Query(None, description="Filter flagged feedback"),
    location: Optional[str] = Query(None, description="Filter by location"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    search: Optional[str] = Query(None, description="Search in text, guest name, or booking ref"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated and filtered list of feedback
    
    Supports filtering by:
    - Channel (web, email, whatsapp, etc.)
    - Status (new, reviewed, resolved, escalated)
    - Priority (low, normal, high, urgent)
    - Sentiment (positive, negative, neutral)
    - Flagged status
    - Location
    - Date range
    - Text search
    """
    try:
        filters = FeedbackFilter(
            channel=channel,
            status=status,
            priority=priority,
            sentiment_label=sentiment_label,
            flagged=flagged,
            location=location,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            size=size
        )
        return await feedback_service.get_feedback_list(db, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_by_id(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific feedback by ID"""
    try:
        feedback = await feedback_service.get_feedback_by_id(db, feedback_id)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")

@router.patch("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    update_data: FeedbackUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update feedback status, priority, or flagged state
    
    Allows updating:
    - Status (new → reviewed → resolved/escalated)
    - Priority level
    - Flagged status
    """
    try:
        feedback = await feedback_service.update_feedback(db, feedback_id, update_data)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating feedback: {str(e)}")

@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics(
    date_from: Optional[datetime] = Query(None, description="Analytics start date"),
    date_to: Optional[datetime] = Query(None, description="Analytics end date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics summary for the specified period
    
    Returns:
    - Sentiment distribution (positive/negative/neutral counts)
    - Top topics with average sentiment
    - Flagged feedback count
    - Overall statistics
    
    Defaults to last 30 days if no date range specified.
    """
    try:
        return await feedback_service.get_analytics(db, date_from, date_to)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@router.get("/alerts/flagged", response_model=List[FeedbackResponse])
async def get_flagged_feedback(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of flagged items"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent flagged feedback for alert dashboard
    
    Returns the most recent feedback that has been automatically flagged
    for urgent attention based on:
    - Very negative sentiment
    - Contains urgent keywords
    - High priority issues
    """
    try:
        return await feedback_service.get_flagged_feedback(db, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving flagged feedback: {str(e)}")

# Health check endpoint for this router
@router.get("/health")
async def health_check():
    """Health check endpoint for feedback API"""
    return {"status": "healthy", "service": "feedback-api"}