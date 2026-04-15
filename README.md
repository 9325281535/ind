# Rubiscape ML Pipeline Tracker

Track ML pipeline execution states with complete audit logging and team collaboration.

## 🎯 Business Goals

- **Save 40% of engineer time** - Eliminate manual status checks (1.2 hours/day per engineer)
- **Eliminate ₹45,000 daily waste** from inefficient pipeline tracking
- **Reduce deployment delays by 50%** through real-time visibility
- **Give managers** complete pipeline overview at a glance

## ✨ Features

### Core Features
- 📊 **Real-time Pipeline Tracking** - Monitor 45+ pipeline statuses simultaneously
- 🔄 **State Management** - Pending → Running → Completed workflow
- 📝 **Complete Audit Trail** - Every action logged with user, IP, timestamp
- 🌍 **Web-based Dashboard** - Accessible from anywhere
- 📱 **Responsive Design** - Works on desktop, tablet, mobile

### Pipeline States
- **PENDING** - Awaiting execution
- **RUNNING** - Currently executing
- **COMPLETED** - Finished successfully
- **FAILED** - Execution failed
- **CANCELLED** - User cancelled

### Pipeline Types
- Data Ingestion
- Model Training
- Deployment

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   React     │◄───────►│   FastAPI    │◄───────►│  PostgreSQL  │
│  Frontend   │ REST API│   Backend    │ SQLAlchemy Async ORM
│  Port 3000  │         │  Port 8000   │         │   Port 5432  │
└─────────────┘         └──────────────┘         └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Docker (optional)

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

### Option 2: Manual Setup

#### Backend
```bash
cd execution-project/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Update .env with your PostgreSQL credentials
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd execution-project/frontend
npm install
npm start
```

## 📊 Dashboard Features

### Summary Cards
- Total pipelines count
- Pipelines by state (Pending, Running, Completed, Failed)
- Success rate percentage

### Pipeline Management
- Create new pipelines
- Start/Complete/Fail pipelines
- Filter by state
- View pipeline metadata
- Action audit trail

### Real-time Updates
- Auto-refresh every 5 seconds
- Live state changes
- Real-time statistics

## 🔌 API Endpoints

### Pipelines
```
GET    /api/v1/pipelines                          - List all
POST   /api/v1/pipelines                          - Create new
GET    /api/v1/pipelines/{id}                     - Get details
PATCH  /api/v1/pipelines/{id}                     - Update state
DELETE /api/v1/pipelines/{id}                     - Cancel
```

### Audit & History
```
GET    /api/v1/pipelines/{id}/state-history       - State transitions
GET    /api/v1/pipelines/{id}/audit-logs          - Action audit logs
```

### Dashboard
```
GET    /api/v1/dashboard/summary                  - Stats summary
```

## 🗄️ Database Schema

### pipelines
```sql
id UUID PRIMARY KEY
name VARCHAR(255) NOT NULL
description TEXT
pipeline_type ENUM (data_ingestion, training, deployment)
current_state ENUM (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
metadata JSONB
created_by VARCHAR(100)
created_at TIMESTAMP
updated_at TIMESTAMP
```

### pipeline_state_history (Immutable)
```sql
Records every state transition with reason
pipeline_id UUID REFERENCES pipelines(id)
from_state → to_state
transition_reason TEXT
triggered_by VARCHAR(100)
created_at TIMESTAMP
```

### audit_logs (Immutable, Append-only)
```sql
pipeline_id UUID REFERENCES pipelines(id)
action VARCHAR(100)
actor VARCHAR(100)
actor_role VARCHAR(50)
changes JSONB
ip_address INET
user_agent TEXT
created_at TIMESTAMP
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Async ORM with support for relationships
- **PostgreSQL** - Reliable relational database
- **Pydantic v2** - Data validation and serialization
- **Alembic** - Database migrations
- **Uvicorn** - ASGI application server

### Frontend
- **React 19** - Modern UI framework
- **CSS Grid/Flexbox** - Responsive layouts
- **Fetch API** - HTTP client
- **ES6+** - Modern JavaScript

## 📈 Metrics & Monitoring

### Dashboard Summary
- Total pipeline count
- Active pipelines
- Success rate calculation
- State distribution

### Audit Trail
- Complete action history
- User tracking
- IP logging
- Timestamp tracking
- Change documentation

## 🔒 Security Features

- SQL injection protection (SQLAlchemy parametrized queries)
- CORS enabled for frontend communication
- Request validation (Pydantic)
- Immutable audit logs (append-only)
- User tracking and IP logging

## 🚀 Deployment

### Local Development
```bash
docker-compose -f docker-compose.yml up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Google Cloud Platform (GCP)
Deploy to production on Google Cloud with Cloud SQL, Cloud Run, and Cloud Storage.

**Quick Start Options:**
1. **[CLOUD_QUICK_START.md](./CLOUD_QUICK_START.md)** - Deploy in 30 minutes
2. **[CLOUD_SETUP.md](./CLOUD_SETUP.md)** - Complete detailed guide
3. **[CLOUD_DEPLOYMENT_CHECKLIST.md](./CLOUD_DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist  
4. **[CLOUD_QUICK_REFERENCE.md](./CLOUD_QUICK_REFERENCE.md)** - Quick command reference
5. **[CLOUD_ARCHITECTURE_GUIDE.md](./CLOUD_ARCHITECTURE_GUIDE.md)** - Visual architecture guide
6. **Automated Script**: `bash deploy-to-gcp.sh` or `deploy-to-gcp.bat`

**Cloud Components:**
- **Frontend**: React app on Cloud Storage + Cloud CDN
- **Backend**: FastAPI on Cloud Run
- **Database**: PostgreSQL on Cloud SQL
- **Estimated Cost**: ~$25-50/month (free tier covers most usage)

See [CLOUD_INTEGRATION_SUMMARY.md](./CLOUD_INTEGRATION_SUMMARY.md) for complete overview.

### Other Platforms
- **Render.com**: Push to GitHub and configure environment variables
- **AWS**: EC2/ECS for backend, RDS for database, S3 for frontend
- **Azure**: App Service for backend, Azure Database for PostgreSQL
- **Docker/Kubernetes**: Use provided Dockerfile and docker-compose.yml

## 📚 Documentation

- **Setup Guide**: See [SETUP.md](./SETUP.md)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Architecture**: See inline code comments

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Submit pull request

## 📝 Sample Data

Create test pipelines via API:
```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Data Pipeline",
    "description": "Daily customer data ingestion",
    "pipeline_type": "data_ingestion",
    "created_by": "engineer@company.com"
  }'
```

## 📊 Business Impact (Projected)

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Time/Engineer/Day | 3 hours | 1.8 hours | 40% savings |
| Daily Waste | ₹45,000 | ₹0 | 100% reduction |
| Pipeline Visibility | Slack/Email | Dashboard | Unified |
| Engineers Impacted | 15 | 15 | Full adoption |

## 🐛 Troubleshooting

### PostgreSQL Connection
```bash
# Check if PostgreSQL is running
psql -U postgres -h localhost

# If using Docker:
docker ps  # See if postgres container is running
```

### API Not Responding
```bash
# Check backend logs
docker-compose logs backend

# Verify database connection
curl http://localhost:8000/health
```

### Frontend Can't Connect
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify proxy in package.json

## 📞 Support

For issues:
1. Check [SETUP.md](./SETUP.md)
2. Review API docs at http://localhost:8000/docs
3. Check logs: `docker-compose logs -f`

## 📄 License

Proprietary - Rubiscape

---

**Status**: Production Ready ✅
**Version**: 1.0.0
**Last Updated**: April 15, 2026
