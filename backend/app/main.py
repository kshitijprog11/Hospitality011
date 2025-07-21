from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import async_engine
from .api.feedback import router as feedback_router
from .nlp.sentiment_analyzer import sentiment_analyzer
from .nlp.topic_extractor import topic_extractor

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting Hospitality Feedback Platform API...")
    
    # Initialize NLP models
    try:
        logger.info("Initializing NLP models...")
        await sentiment_analyzer.initialize()
        await topic_extractor.initialize()
        logger.info("NLP models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLP models: {e}")
        logger.warning("Some NLP features may not work properly")
    
    # Test database connection
    try:
        async with async_engine.begin() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await async_engine.dispose()
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Hospitality Feedback & Sentiment Analysis Platform",
    description="""
    A comprehensive platform for hospitality businesses to collect, analyze, and manage guest feedback using AI.
    
    ## Features
    
    * **Automatic Sentiment Analysis**: AI-powered sentiment detection using state-of-the-art models
    * **Topic Extraction**: Automatically identify key topics and themes in feedback
    * **Smart Flagging**: Urgent issues are automatically flagged for immediate attention
    * **Multi-channel Support**: Collect feedback from web, email, social media, and review platforms
    * **Real-time Analytics**: Comprehensive dashboards with sentiment trends and insights
    * **Alert System**: Get notified of critical issues as they happen
    
    ## API Usage
    
    This API provides endpoints for:
    - Creating and managing feedback entries
    - Retrieving filtered and paginated feedback lists
    - Getting analytics and reports
    - Managing alerts and flagged content
    
    All feedback is automatically processed through our NLP pipeline to extract sentiment,
    topics, and urgency indicators.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Include routers
app.include_router(feedback_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Welcome endpoint with API information
    """
    return {
        "message": "Welcome to the Hospitality Feedback & Sentiment Analysis Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "AI-powered sentiment analysis",
            "Automatic topic extraction", 
            "Smart flagging system",
            "Multi-channel feedback collection",
            "Real-time analytics",
            "Alert management"
        ]
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Test database connection
        async with async_engine.begin() as conn:
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "database": db_status,
        "nlp_models": {
            "sentiment_analyzer": "loaded" if sentiment_analyzer.sentiment_pipeline else "fallback",
            "topic_extractor": "loaded" if topic_extractor.keybert_model else "basic"
        },
        "version": "1.0.0"
    }

# Metrics endpoint (for monitoring)
@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """
    Basic metrics endpoint for monitoring
    """
    return {
        "api_version": "1.0.0",
        "environment": "development" if settings.debug else "production",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )