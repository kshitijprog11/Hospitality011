from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from ..models.feedback import Feedback
from ..models.schemas import (
    FeedbackCreate, FeedbackUpdate, FeedbackFilter, 
    FeedbackResponse, FeedbackList, AnalyticsResponse,
    SentimentDistribution, TopicAnalysis
)
from ..nlp.sentiment_analyzer import sentiment_analyzer
from ..nlp.topic_extractor import topic_extractor

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        pass
    
    async def create_feedback(
        self, 
        db: AsyncSession, 
        feedback_data: FeedbackCreate
    ) -> FeedbackResponse:
        """Create new feedback with NLP analysis"""
        try:
            # Create feedback instance
            feedback = Feedback(
                text=feedback_data.text,
                channel=feedback_data.channel.value,
                page=feedback_data.page,
                guest_name=feedback_data.guest_name,
                guest_contact=feedback_data.guest_contact,
                booking_reference=feedback_data.booking_reference,
                location=feedback_data.location
            )
            
            # Add to database first
            db.add(feedback)
            await db.flush()  # Get the ID
            
            # Perform NLP analysis
            await self._analyze_feedback(feedback)
            
            # Mark as processed
            feedback.processed = True
            
            # Commit to database
            await db.commit()
            await db.refresh(feedback)
            
            logger.info(f"Created feedback {feedback.id} with sentiment {feedback.sentiment}")
            
            return FeedbackResponse.model_validate(feedback)
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            await db.rollback()
            raise
    
    async def _analyze_feedback(self, feedback: Feedback) -> None:
        """Perform NLP analysis on feedback"""
        try:
            # Analyze sentiment
            sentiment_result = await sentiment_analyzer.analyze_sentiment(feedback.text)
            
            feedback.sentiment = sentiment_result['sentiment']
            feedback.sentiment_label = sentiment_result['sentiment_label']
            feedback.confidence = sentiment_result['confidence']
            feedback.flagged = sentiment_result['flagged']
            
            # Set priority based on sentiment and flagging
            if feedback.flagged:
                if feedback.sentiment <= -0.8:
                    feedback.priority = "urgent"
                elif feedback.sentiment <= -0.5:
                    feedback.priority = "high"
                else:
                    feedback.priority = "normal"
            else:
                feedback.priority = "normal"
            
            # Extract topics
            topic_result = await topic_extractor.extract_topics(feedback.text)
            feedback.topics = topic_result['topics']
            
            logger.debug(f"Analysis complete for feedback {feedback.id}: "
                        f"sentiment={feedback.sentiment}, topics={feedback.topics}")
            
        except Exception as e:
            logger.error(f"Error analyzing feedback {feedback.id}: {e}")
            feedback.processing_error = str(e)
    
    async def get_feedback_list(
        self, 
        db: AsyncSession, 
        filters: FeedbackFilter
    ) -> FeedbackList:
        """Get paginated and filtered feedback list"""
        try:
            # Build query
            query = select(Feedback)
            
            # Apply filters
            conditions = []
            
            if filters.channel:
                conditions.append(Feedback.channel == filters.channel.value)
            
            if filters.status:
                conditions.append(Feedback.status == filters.status.value)
            
            if filters.priority:
                conditions.append(Feedback.priority == filters.priority.value)
            
            if filters.sentiment_label:
                conditions.append(Feedback.sentiment_label == filters.sentiment_label.value)
            
            if filters.flagged is not None:
                conditions.append(Feedback.flagged == filters.flagged)
            
            if filters.location:
                conditions.append(Feedback.location.ilike(f"%{filters.location}%"))
            
            if filters.date_from:
                conditions.append(Feedback.created_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(Feedback.created_at <= filters.date_to)
            
            if filters.search:
                search_condition = or_(
                    Feedback.text.ilike(f"%{filters.search}%"),
                    Feedback.guest_name.ilike(f"%{filters.search}%"),
                    Feedback.booking_reference.ilike(f"%{filters.search}%")
                )
                conditions.append(search_condition)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Count total items
            count_query = select(func.count(Feedback.id)).where(and_(*conditions)) if conditions else select(func.count(Feedback.id))
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply ordering
            query = query.order_by(desc(Feedback.created_at))
            
            # Apply pagination
            offset = (filters.page - 1) * filters.size
            query = query.offset(offset).limit(filters.size)
            
            # Execute query
            result = await db.execute(query)
            feedback_items = result.scalars().all()
            
            # Calculate pagination info
            pages = (total + filters.size - 1) // filters.size
            
            return FeedbackList(
                items=[FeedbackResponse.model_validate(item) for item in feedback_items],
                total=total,
                page=filters.page,
                size=filters.size,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error getting feedback list: {e}")
            raise
    
    async def get_feedback_by_id(
        self, 
        db: AsyncSession, 
        feedback_id: int
    ) -> Optional[FeedbackResponse]:
        """Get feedback by ID"""
        try:
            query = select(Feedback).where(Feedback.id == feedback_id)
            result = await db.execute(query)
            feedback = result.scalar_one_or_none()
            
            if feedback:
                return FeedbackResponse.model_validate(feedback)
            return None
            
        except Exception as e:
            logger.error(f"Error getting feedback {feedback_id}: {e}")
            raise
    
    async def update_feedback(
        self, 
        db: AsyncSession, 
        feedback_id: int, 
        update_data: FeedbackUpdate
    ) -> Optional[FeedbackResponse]:
        """Update feedback"""
        try:
            query = select(Feedback).where(Feedback.id == feedback_id)
            result = await db.execute(query)
            feedback = result.scalar_one_or_none()
            
            if not feedback:
                return None
            
            # Update fields
            if update_data.status is not None:
                feedback.status = update_data.status.value
            
            if update_data.priority is not None:
                feedback.priority = update_data.priority.value
            
            if update_data.flagged is not None:
                feedback.flagged = update_data.flagged
            
            feedback.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(feedback)
            
            return FeedbackResponse.model_validate(feedback)
            
        except Exception as e:
            logger.error(f"Error updating feedback {feedback_id}: {e}")
            await db.rollback()
            raise
    
    async def get_analytics(
        self, 
        db: AsyncSession, 
        date_from: Optional[datetime] = None, 
        date_to: Optional[datetime] = None
    ) -> AnalyticsResponse:
        """Get analytics for the specified period"""
        try:
            if not date_from:
                date_from = datetime.utcnow() - timedelta(days=30)
            if not date_to:
                date_to = datetime.utcnow()
            
            # Base query with date filter
            base_query = select(Feedback).where(
                and_(
                    Feedback.created_at >= date_from,
                    Feedback.created_at <= date_to
                )
            )
            
            # Get all feedback for the period
            result = await db.execute(base_query)
            all_feedback = result.scalars().all()
            
            # Calculate sentiment distribution
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            sentiment_sum = 0.0
            flagged_count = 0
            
            for feedback in all_feedback:
                if feedback.sentiment_label:
                    sentiment_counts[feedback.sentiment_label] += 1
                if feedback.sentiment is not None:
                    sentiment_sum += feedback.sentiment
                if feedback.flagged:
                    flagged_count += 1
            
            total_feedback = len(all_feedback)
            average_sentiment = sentiment_sum / total_feedback if total_feedback > 0 else 0.0
            
            sentiment_distribution = SentimentDistribution(
                positive=sentiment_counts['positive'],
                negative=sentiment_counts['negative'],
                neutral=sentiment_counts['neutral'],
                total=total_feedback
            )
            
            # Extract top topics
            all_topics = []
            topic_sentiments = {}
            
            for feedback in all_feedback:
                if feedback.topics:
                    for topic in feedback.topics:
                        all_topics.append(topic)
                        if topic not in topic_sentiments:
                            topic_sentiments[topic] = []
                        if feedback.sentiment is not None:
                            topic_sentiments[topic].append(feedback.sentiment)
            
            # Count topics and calculate average sentiment
            from collections import Counter
            topic_counts = Counter(all_topics)
            
            top_topics = []
            for topic, count in topic_counts.most_common(10):
                avg_sentiment = sum(topic_sentiments[topic]) / len(topic_sentiments[topic]) if topic_sentiments[topic] else 0.0
                top_topics.append(TopicAnalysis(
                    topic=topic,
                    count=count,
                    sentiment_avg=round(avg_sentiment, 3)
                ))
            
            return AnalyticsResponse(
                sentiment_distribution=sentiment_distribution,
                top_topics=top_topics,
                flagged_count=flagged_count,
                total_feedback=total_feedback,
                average_sentiment=round(average_sentiment, 3),
                period_start=date_from,
                period_end=date_to
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise
    
    async def get_flagged_feedback(
        self, 
        db: AsyncSession, 
        limit: int = 10
    ) -> List[FeedbackResponse]:
        """Get recent flagged feedback for alerts"""
        try:
            query = (
                select(Feedback)
                .where(Feedback.flagged == True)
                .order_by(desc(Feedback.created_at))
                .limit(limit)
            )
            
            result = await db.execute(query)
            flagged_feedback = result.scalars().all()
            
            return [FeedbackResponse.model_validate(feedback) for feedback in flagged_feedback]
            
        except Exception as e:
            logger.error(f"Error getting flagged feedback: {e}")
            raise

# Global service instance
feedback_service = FeedbackService()