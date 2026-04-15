# Google Cloud Platform Setup Guide

Complete guide to deploy Rubiscape ML Pipeline Tracker to Google Cloud Platform (GCP).

## 📋 Prerequisites

1. **Google Cloud Account** - [Create one](https://cloud.google.com)
2. **GCP Project** - Create a new project
3. **gcloud CLI** - [Install here](https://cloud.google.com/sdk/docs/install)
4. **Local setup complete** - Backend and frontend working locally

## 🏗️ GCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │  Cloud Run       │◄───────►│  Cloud SQL       │           │
│  │  (FastAPI)       │         │  (PostgreSQL)    │           │
│  │  Port 8000       │         │                  │           │
│  └──────────────────┘         └──────────────────┘           │
│          ▲                                                    │
│          │                                                    │
│  ┌──────────────────┐                                        │
│  │ Cloud Storage    │                                        │
│  │ + Cloud CDN      │                                        │
│  │  (React build)   │                                        │
│  │  Port 3000       │                                        │
│  └──────────────────┘                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Initial Setup

### 1.1 Create GCP Project
```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID

# Set it as active
gcloud config set project $PROJECT_ID
```

### 1.2 Enable Required APIs
```bash
gcloud services enable \
  cloudsql.googleapis.com \
  sqladmin.googleapis.com \
  run.googleapis.com \
  storage-api.googleapis.com \
  compute.googleapis.com \
  containerregistry.googleapis.com
```

### 1.3 Set Up Authentication
```bash
# Authenticate with GCP
gcloud auth login

# Set default region
gcloud config set compute/region $REGION
```

## Step 2: Set Up Cloud SQL (PostgreSQL)

### 2.1 Create Cloud SQL Instance
```bash
# Create PostgreSQL instance
gcloud sql instances create rubiscape-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --authorized-networks=0.0.0.0/0 \
  --database-flags cloudsql_iam_authentication=on \
  --backup-start-time=03:00 \
  --enable-bin-log

# Wait for creation (3-5 minutes)
```

### 2.2 Create Database and User
```bash
# Create database
gcloud sql databases create rubiscape_ml \
  --instance=rubiscape-db

# Create database user (password method)
gcloud sql users create postgres \
  --instance=rubiscape-db \
  --password=YOUR_SECURE_PASSWORD_HERE
```

### 2.3 Get Connection String
```bash
# Get the public IP
gcloud sql instances describe rubiscape-db \
  --format='value(ipAddresses[0].ipAddress)'

# Connection string format:
# postgresql://postgres:PASSWORD@PUBLIC_IP:5432/rubiscape_ml
```

## Step 3: Prepare Backend for Cloud Run

### 3.1 Update Backend Configuration

Create `.env.cloud` in `backend/` directory:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@CLOUD_SQL_IP:5432/rubiscape_ml
SECRET_KEY=use-a-strong-random-secret-key-here
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 3.2 Create Dockerfile (Already exists, verify it's correct)

Check `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.3 Update requirements.txt
Ensure these are included:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

## Step 4: Build and Deploy Backend

### 4.1 Configure Docker for GCP
```bash
# Configure authentication
gcloud auth configure-docker

# Set image name
export IMAGE_NAME="gcr.io/$PROJECT_ID/rubiscape-backend"
```

### 4.2 Build and Push Docker Image
```bash
cd backend

# Build image
docker build -t $IMAGE_NAME .

# Push to Google Container Registry
docker push $IMAGE_NAME
```

### 4.3 Deploy to Cloud Run
```bash
gcloud run deploy rubiscape-backend \
  --image=$IMAGE_NAME \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600 \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@CLOUD_SQL_IP:5432/rubiscape_ml,SECRET_KEY=YOUR_SECRET_KEY,ENVIRONMENT=production"

# Get backend URL
gcloud run services describe rubiscape-backend --region=$REGION --format='value(status.url)'
```

## Step 5: Build and Deploy Frontend

### 5.1 Update Frontend Configuration

Create `.env.production` in `frontend/`:
```env
REACT_APP_API_URL=https://your-backend-url.run.app/api/v1
```

### 5.2 Build React Application
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 5.3 Upload to Cloud Storage

```bash
# Create storage bucket
gsutil mb gs://$PROJECT_ID-frontend/

# Upload build files
gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/

# Make public (optional, if using public access)
gsutil iam ch serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com:roles/storage.objectViewer gs://$PROJECT_ID-frontend

# Set index.html to serve for 404s
gsutil web set -m index.html -e index.html gs://$PROJECT_ID-frontend

# View URL
echo "Frontend URL: https://storage.googleapis.com/$PROJECT_ID-frontend/index.html"
```

### 5.4 (Optional) Set Up Cloud CDN

```bash
# Create Load Balancer with Cloud CDN
# Manual setup in Cloud Console:
# 1. Go to Cloud CDN
# 2. Create new CDN policy
# 3. Point to Cloud Storage bucket
# 4. Get CDN URL
```

## Step 6: Connect Backend to Cloud SQL

### 6.1 Network Configuration

```bash
# Get Cloud SQL connection name
gcloud sql instances describe rubiscape-db \
  --format='value(connectionName)'
# Format: PROJECT_ID:REGION:INSTANCE_NAME
```

### 6.2 Update Cloud Run Environment Variables

```bash
gcloud run services update rubiscape-backend \
  --region=$REGION \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@CLOUD_SQL_IP:5432/rubiscape_ml"
```

## Step 7: Update CORS Settings

### 7.1 Update Backend CORS

Edit `backend/app/main.py`:
```python
import os

# Get allowed origins from environment
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.2 Update Cloud Run Backend with Frontend URL

```bash
gcloud run services update rubiscape-backend \
  --set-env-vars="ALLOWED_ORIGINS=https://storage.googleapis.com/$PROJECT_ID-frontend" \
  --region=$REGION
```

## Step 8: Database Initialization

### 8.1 Connect to Cloud SQL (From Local Machine)

```bash
# Install Cloud SQL Proxy
gcloud components install cloud_sql_proxy

# Connect
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432

# In another terminal, run migrations
export DATABASE_URL="postgresql://postgres:PASSWORD@localhost:5432/rubiscape_ml"
python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"
```

## Step 9: Monitoring & Logging

### 9.1 View Backend Logs
```bash
gcloud run logs read rubiscape-backend --region=$REGION --limit=50
```

### 9.2 Monitor Cloud SQL
```bash
gcloud sql operations list --instance=rubiscape-db
```

### 9.3 Set Up Alerts
- Go to Cloud Console → Monitoring → Create Policy
- Set alerts for CPU, Memory, Network usage

## Step 10: Domain & SSL (Optional)

### 10.1 Use Custom Domain
```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service=rubiscape-backend \
  --domain=api.yourdomain.com \
  --region=$REGION
```

### 10.2 SSL Certificate
- Google Cloud automatically handles SSL for Cloud Run
- Use Cloud Armor for additional security

## 📊 Cost Estimates (Monthly)

- **Cloud SQL (db-f1-micro)**: ~$15-20
- **Cloud Run (512MB, 1 CPU)**: ~$10-20 (based on usage)
- **Cloud Storage**: ~$0.10-1
- **Cloud CDN**: Free tier + ~$0.12 per GB

**Total**: ~$25-50/month (free tier coverage)

## 🔧 Environment Variables Quick Reference

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@IP:5432/rubiscape_ml
SECRET_KEY=your-secret-key
ENVIRONMENT=production
ALLOWED_ORIGINS=https://storage.googleapis.com/$PROJECT_ID-frontend

# Frontend
REACT_APP_API_URL=https://your-backend-url.run.app/api/v1
```

## 🆘 Troubleshooting

### Backend can't connect to Cloud SQL
- Check firewall rules: `gcloud sql instances describe rubiscape-db --format='value(ipAddresses)'`
- Verify password is correct
- Check Cloud SQL user exists: `gcloud sql users list --instance=rubiscape-db`

### Frontend not loading
- Check bucket permissions: `gsutil iam get gs://$PROJECT_ID-frontend`
- Verify CORS settings in backend
- Check browser console for API errors

### High latency
- Enable Cloud CDN for static files
- Use Cloud SQL Read Replicas for scaling
- Check Cloud Run memory allocation

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)

## ✅ Deployment Checklist

- [ ] GCP Project created and APIs enabled
- [ ] Cloud SQL instance created with PostgreSQL
- [ ] Database and user created in Cloud SQL
- [ ] Backend Dockerfile tested locally
- [ ] Backend Docker image built and pushed to GCR
- [ ] Backend deployed to Cloud Run
- [ ] Backend connected to Cloud SQL
- [ ] Frontend built successfully
- [ ] Frontend uploaded to Cloud Storage
- [ ] CORS and firewall rules configured
- [ ] Custom domain mapped (if using custom domain)
- [ ] Monitoring and logging set up
- [ ] Database initialized with tables

---

**Next Steps**: Follow each step in order. Start with Step 1 and work through to Step 10.
