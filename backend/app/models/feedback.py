from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    channel = Column(String(100), nullable=False)  # e.g., "web", "email", "whatsapp", "google_reviews"
    page = Column(String(200), nullable=True)  # Which page/service the feedback is about
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # NLP Analysis Results
    sentiment = Column(Float, nullable=True)  # -1 to 1 scale
    sentiment_label = Column(String(20), nullable=True)  # "positive", "negative", "neutral"
    confidence = Column(Float, nullable=True)  # Confidence score of sentiment analysis
    topics = Column(JSON, nullable=True)  # Array of extracted topics/keywords
    
    # Alert and Status Management
    flagged = Column(Boolean, default=False)  # Automatically flagged for urgent attention
    status = Column(String(20), default="new")  # "new", "reviewed", "resolved", "escalated"
    priority = Column(String(10), default="normal")  # "low", "normal", "high", "urgent"
    
    # Metadata
    guest_name = Column(String(100), nullable=True)  # First name only for privacy
    guest_contact = Column(String(200), nullable=True)  # Masked/encrypted contact info
    booking_reference = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)  # Hotel/restaurant location
    
    # Analysis metadata
    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, sentiment={self.sentiment}, flagged={self.flagged})>"