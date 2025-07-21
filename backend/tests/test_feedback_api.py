import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime

from app.main import app
from app.core.database import Base, get_db
from app.models.feedback import Feedback

# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
async def async_client():
    """Create test client and database"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing"""
    return {
        "text": "The service was excellent and the room was very clean. Great experience!",
        "channel": "web",
        "page": "booking-confirmation",
        "guest_name": "John",
        "booking_reference": "BK123456",
        "location": "Hotel Downtown"
    }

@pytest.fixture
def negative_feedback_data():
    """Negative feedback data for testing flagging"""
    return {
        "text": "This is terrible! The room was dirty and the service was awful. Very urgent issue!",
        "channel": "email",
        "guest_name": "Jane",
        "booking_reference": "BK789012"
    }

class TestFeedbackAPI:
    
    @pytest.mark.asyncio
    async def test_create_feedback_success(self, async_client: AsyncClient, sample_feedback_data):
        """Test successful feedback creation"""
        response = await async_client.post("/api/feedback/", json=sample_feedback_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["text"] == sample_feedback_data["text"]
        assert data["channel"] == sample_feedback_data["channel"]
        assert data["guest_name"] == sample_feedback_data["guest_name"]
        assert data["processed"] == True
        assert "sentiment" in data
        assert "topics" in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_feedback_negative_flagging(self, async_client: AsyncClient, negative_feedback_data):
        """Test that negative feedback gets flagged"""
        response = await async_client.post("/api/feedback/", json=negative_feedback_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Should be flagged due to negative sentiment and keywords
        assert data["flagged"] == True
        assert data["priority"] in ["high", "urgent"]
        assert data["sentiment"] < 0  # Should be negative
    
    @pytest.mark.asyncio
    async def test_create_feedback_validation_error(self, async_client: AsyncClient):
        """Test feedback creation with invalid data"""
        invalid_data = {
            "text": "",  # Empty text should fail validation
            "channel": "web"
        }
        
        response = await async_client.post("/api/feedback/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_feedback_list(self, async_client: AsyncClient, sample_feedback_data):
        """Test getting feedback list"""
        # Create some feedback first
        await async_client.post("/api/feedback/", json=sample_feedback_data)
        
        response = await async_client.get("/api/feedback/")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_feedback_list_filtering(self, async_client: AsyncClient, sample_feedback_data, negative_feedback_data):
        """Test feedback list filtering"""
        # Create different types of feedback
        await async_client.post("/api/feedback/", json=sample_feedback_data)
        await async_client.post("/api/feedback/", json=negative_feedback_data)
        
        # Test channel filter
        response = await async_client.get("/api/feedback/?channel=web")
        assert response.status_code == 200
        data = response.json()
        assert all(item["channel"] == "web" for item in data["items"])
        
        # Test flagged filter
        response = await async_client.get("/api/feedback/?flagged=true")
        assert response.status_code == 200
        data = response.json()
        assert all(item["flagged"] == True for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_id(self, async_client: AsyncClient, sample_feedback_data):
        """Test getting specific feedback by ID"""
        # Create feedback
        create_response = await async_client.post("/api/feedback/", json=sample_feedback_data)
        created_feedback = create_response.json()
        feedback_id = created_feedback["id"]
        
        # Get by ID
        response = await async_client.get(f"/api/feedback/{feedback_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == feedback_id
        assert data["text"] == sample_feedback_data["text"]
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_id_not_found(self, async_client: AsyncClient):
        """Test getting non-existent feedback"""
        response = await async_client.get("/api/feedback/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_feedback(self, async_client: AsyncClient, sample_feedback_data):
        """Test updating feedback status"""
        # Create feedback
        create_response = await async_client.post("/api/feedback/", json=sample_feedback_data)
        created_feedback = create_response.json()
        feedback_id = created_feedback["id"]
        
        # Update status
        update_data = {"status": "reviewed", "priority": "high"}
        response = await async_client.patch(f"/api/feedback/{feedback_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reviewed"
        assert data["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_get_analytics(self, async_client: AsyncClient, sample_feedback_data, negative_feedback_data):
        """Test analytics endpoint"""
        # Create some feedback
        await async_client.post("/api/feedback/", json=sample_feedback_data)
        await async_client.post("/api/feedback/", json=negative_feedback_data)
        
        response = await async_client.get("/api/feedback/analytics/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "sentiment_distribution" in data
        assert "top_topics" in data
        assert "total_feedback" in data
        assert "average_sentiment" in data
        assert data["total_feedback"] >= 2
    
    @pytest.mark.asyncio
    async def test_get_flagged_feedback(self, async_client: AsyncClient, negative_feedback_data):
        """Test getting flagged feedback"""
        # Create flagged feedback
        await async_client.post("/api/feedback/", json=negative_feedback_data)
        
        response = await async_client.get("/api/feedback/alerts/flagged")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(item["flagged"] == True for item in data)
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test feedback API health check"""
        response = await async_client.get("/api/feedback/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "feedback-api"

class TestRootEndpoints:
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint"""
        response = await async_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "nlp_models" in data
        assert "version" in data

if __name__ == "__main__":
    pytest.main([__file__])