# 🏨 Hospitality Feedback & Sentiment Analysis Platform

A comprehensive AI-powered platform for hospitality businesses to collect, analyze, and manage guest feedback using advanced sentiment analysis and topic extraction.

## ✨ Features

### 🤖 AI-Powered Analysis
- **Sentiment Analysis**: State-of-the-art sentiment detection using Hugging Face Transformers
- **Topic Extraction**: Automatic identification of key themes using KeyBERT and spaCy
- **Smart Flagging**: Urgent issues automatically flagged for immediate attention
- **Multi-language Support**: Expandable to support multiple languages

### 📊 Real-time Analytics
- **Sentiment Distribution**: Visual representation of positive, negative, and neutral feedback
- **Topic Trends**: Track what guests are talking about most
- **Performance Metrics**: KPIs and trend analysis
- **Custom Reporting**: Export reports in multiple formats

### 🔔 Alert System
- **Instant Notifications**: Real-time alerts for critical issues
- **Priority Levels**: Automatic prioritization based on sentiment and keywords
- **Dashboard Alerts**: Centralized alert management
- **Email Integration**: Optional email notifications for urgent issues

### 🌐 Multi-channel Support
- **Web Forms**: Direct feedback collection
- **Email Integration**: Process feedback from email channels
- **Social Media**: Monitor mentions and reviews
- **Review Platforms**: Integration with booking sites and review platforms

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on all devices
- **Beautiful Charts**: Interactive visualizations using Recharts
- **Dark Mode**: Optional dark theme support
- **Accessibility**: WCAG 2.1 compliant interface

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- PostgreSQL 15+ (if running locally)

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd feedback-sentiment-platform
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the platform**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### 🛠️ Development Setup

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment variables
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📁 Project Structure

```
feedback-sentiment-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── nlp/           # NLP processing
│   │   └── main.py        # Application entry point
│   ├── migrations/        # Database migrations
│   ├── tests/            # Unit tests
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── styles/      # CSS styles
│   └── package.json     # Node.js dependencies
├── docs/                # Documentation
├── .github/workflows/   # CI/CD pipelines
├── docker-compose.yml   # Docker orchestration
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables for configuration:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/feedback_platform

# API Keys
OPENAI_API_KEY=your_openai_key_here
HUGGING_FACE_API_KEY=your_hugging_face_key_here

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# NLP Configuration
SENTIMENT_THRESHOLD_NEGATIVE=-0.5
SENTIMENT_THRESHOLD_POSITIVE=0.5
FLAGGED_KEYWORDS=urgent,emergency,terrible,awful,disgusting,worst

# Notifications
ENABLE_EMAIL_ALERTS=True
ALERT_THRESHOLD_SENTIMENT=-0.7
```

## 📚 API Documentation

### REST API Endpoints

#### Feedback Management
- `POST /api/feedback/` - Create new feedback
- `GET /api/feedback/` - List feedback with filters
- `GET /api/feedback/{id}` - Get specific feedback
- `PATCH /api/feedback/{id}` - Update feedback status

#### Analytics
- `GET /api/feedback/analytics/summary` - Get analytics summary
- `GET /api/feedback/alerts/flagged` - Get flagged feedback

#### Health Checks
- `GET /health` - Application health status
- `GET /api/feedback/health` - Feedback service health

### Example Usage

**Create Feedback:**
```bash
curl -X POST "http://localhost:8000/api/feedback/" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "The service was excellent and the room was very clean!",
       "channel": "web",
       "guest_name": "John",
       "location": "Hotel Downtown"
     }'
```

**Get Analytics:**
```bash
curl "http://localhost:8000/api/feedback/analytics/summary"
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 📈 Monitoring & Analytics

### Key Metrics Tracked
- **Sentiment Distribution**: Percentage of positive, negative, neutral feedback
- **Topic Analysis**: Most discussed topics and their sentiment
- **Response Times**: How quickly issues are addressed
- **Channel Performance**: Feedback volume and sentiment by channel
- **Alert Resolution**: Time to resolve flagged issues

### Dashboards Available
1. **Executive Dashboard**: High-level KPIs and trends
2. **Operations Dashboard**: Detailed feedback management
3. **Analytics Dashboard**: Deep-dive into sentiment and topics
4. **Alerts Dashboard**: Real-time issue monitoring

## 🔒 Security & Privacy

### Data Protection
- **PII Masking**: Personal information is automatically masked
- **Secure Storage**: All data encrypted at rest
- **Access Control**: Role-based permissions
- **Audit Logging**: Comprehensive activity tracking

### Compliance
- **GDPR Ready**: Built-in privacy controls
- **Data Retention**: Configurable retention policies
- **Anonymization**: Personal data can be anonymized
- **Export Controls**: Easy data export for compliance

## 🚀 Deployment

### Production Deployment

1. **Set up environment variables** for production
2. **Configure database** with proper credentials
3. **Set up SSL certificates** for HTTPS
4. **Configure monitoring** and logging
5. **Deploy using Docker Compose** or Kubernetes

### Scaling Considerations
- **Database**: Use PostgreSQL with read replicas
- **Caching**: Redis for session and query caching
- **Load Balancing**: Nginx or cloud load balancer
- **Background Processing**: Celery workers for heavy NLP tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Write tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Project Wiki](docs/)
- **Issues**: [GitHub Issues](issues/)
- **Discussions**: [GitHub Discussions](discussions/)

## 🙏 Acknowledgments

- **Hugging Face** for providing excellent NLP models
- **FastAPI** for the amazing web framework
- **React** and **Tailwind CSS** for the beautiful UI
- **PostgreSQL** for reliable data storage

---

**Built with ❤️ for the hospitality industry**
