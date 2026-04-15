# Cloud Deployment - Quick Reference

Fast lookup guide for cloud deployment commands and configurations.

## 🚀 Quick Commands

### GCP Setup
```bash
# Login
gcloud auth login

# Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable cloudsql.googleapis.com run.googleapis.com storage-api.googleapis.com
```

### Cloud SQL (PostgreSQL)
```bash
# Create instance
gcloud sql instances create rubiscape-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create rubiscape_ml --instance=rubiscape-db

# Create user
gcloud sql users create postgres --instance=rubiscape-db --password=$DB_PASSWORD

# Get IP
gcloud sql instances describe rubiscape-db --format='value(ipAddresses[0].ipAddress)'

# Connect
gcloud sql connect rubiscape-db --user=postgres
```

### Backend Deployment
```bash
# Build Docker image
cd backend
docker build -t gcr.io/$PROJECT_ID/rubiscape-backend .

# Push to registry
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/rubiscape-backend

# Deploy to Cloud Run
gcloud run deploy rubiscape-backend \
  --image=gcr.io/$PROJECT_ID/rubiscape-backend \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:$DB_PASSWORD@$DB_IP:5432/rubiscape_ml,SECRET_KEY=$SECRET_KEY,ENVIRONMENT=production"

# Get URL
gcloud run services describe rubiscape-backend --region=$REGION --format='value(status.url)'
```

### Frontend Deployment
```bash
# Build
cd frontend
npm install
REACT_APP_API_URL=$BACKEND_URL/api/v1 npm run build

# Upload to Cloud Storage
gsutil mb gs://$PROJECT_ID-frontend
gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/
gsutil web set -m index.html -e index.html gs://$PROJECT_ID-frontend
```

## 📊 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@IP:5432/rubiscape_ml
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
ALLOWED_ORIGINS=https://storage.googleapis.com/$PROJECT_ID-frontend
LOG_LEVEL=info
DB_POOL_SIZE=20
```

### Frontend (.env.production)
```env
REACT_APP_API_URL=https://backend-url.run.app/api/v1
```

## 📝 File Locations

| File | Purpose | Location |
|------|---------|----------|
| Complete Guide | Full step-by-step with all details | [CLOUD_SETUP.md](CLOUD_SETUP.md) |
| Quick Start | 30-min deployment guide | [CLOUD_QUICK_START.md](CLOUD_QUICK_START.md) |
| Checklist | Progress tracking checklist | [CLOUD_DEPLOYMENT_CHECKLIST.md](CLOUD_DEPLOYMENT_CHECKLIST.md) |
| Summary | Overview of all resources | [CLOUD_INTEGRATION_SUMMARY.md](CLOUD_INTEGRATION_SUMMARY.md) |
| This Guide | Quick reference | [CLOUD_QUICK_REFERENCE.md](CLOUD_QUICK_REFERENCE.md) |
| Deploy Script | Automated deployment (Linux/Mac) | [deploy-to-gcp.sh](deploy-to-gcp.sh) |
| Deploy Script | Automated deployment (Windows) | [deploy-to-gcp.bat](deploy-to-gcp.bat) |
| Env Example | Backend env variables | [backend/.env.example](backend/.env.example) |
| Cloud DB Config | Cloud-optimized database module | [backend/app/database_cloud.py](backend/app/database_cloud.py) |
| Cloud App | Cloud-ready FastAPI app | [backend/app/main_cloud.py](backend/app/main_cloud.py) |

## 🔗 API Endpoints

### Health & Status
- `GET /health` - Liveness check
- `GET /ready` - Readiness check
- `GET /` - Root endpoint

### API Routes
All routes prefixed with `/api/v1/`
- See backend routes in [backend/app/routes.py](../backend/app/routes.py)

## 🆘 Common Issues & Fixes

### Backend won't connect to database
```bash
# Check Cloud SQL IP
gcloud sql instances describe rubiscape-db --format='value(ipAddresses[0].ipAddress)'

# Verify password
gcloud sql users describe postgres --instance=rubiscape-db

# Check firewall
gcloud sql instances describe rubiscape-db --format='value(settings.ipConfiguration)'

# Verify connection string format
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@IP:5432/rubiscape_ml
```

### Frontend not loading
```bash
# Check bucket exists and has files
gsutil ls gs://$PROJECT_ID-frontend

# Verify index.html is there
gsutil ls gs://$PROJECT_ID-frontend/index.html

# Check buckets
gsutil ls
```

### CORS errors
```bash
# Update allowed origins
gcloud run services update rubiscape-backend \
  --set-env-vars="ALLOWED_ORIGINS=https://storage.googleapis.com/$PROJECT_ID-frontend" \
  --region=$REGION

# Verify setting
gcloud run services describe rubiscape-backend --region=$REGION
```

### High latency
```bash
# Check Cloud Run memory
gcloud run services describe rubiscape-backend --region=$REGION --format='value(spec.template.spec.containers[0].resources.limits.memory)'

# Increase if needed
gcloud run services update rubiscape-backend \
  --memory=1Gi \
  --region=$REGION

# Enable Cloud CDN (for frontend)
# Manual task in Cloud Console > Cloud CDN
```

## 📊 Monitoring Commands

```bash
# View backend logs
gcloud run logs read rubiscape-backend --region=$REGION --limit=50

# View recent errors
gcloud run logs read rubiscape-backend --region=$REGION --limit=100 | grep -i error

# Check service status
gcloud run services describe rubiscape-backend --region=$REGION

# List running services
gcloud run services list --region=$REGION

# Check Cloud SQL status
gcloud sql instances describe rubiscape-db

# Check database size
gcloud sql operations list --instance=rubiscape-db --limit=10
```

## 🗑️ Cleanup Commands

```bash
# Delete Cloud Run service
gcloud run services delete rubiscape-backend --region=$REGION --quiet

# Delete Cloud SQL instance
gcloud sql instances delete rubiscape-db --quiet

# Delete Cloud Storage bucket
gsutil -r rm gs://$PROJECT_ID-frontend

# Delete Docker image
gcloud container images delete gcr.io/$PROJECT_ID/rubiscape-backend --quiet

# Delete entire project (WARNING: Can't undo!)
gcloud projects delete $PROJECT_ID --quiet
```

## 💰 Cost Tracking

```bash
# View billing info
gcloud billing accounts list

# Check project billing
gcloud billing projects describe $PROJECT_ID

# View quotas
gcloud compute project-info describe --project=$PROJECT_ID | grep QUOTA

# Check resource usage
gcloud monitoring time-series list --filter='resource.type="cloud_run_revision"'
```

## 🔐 Security Commands

```bash
# List IAM members
gcloud projects get-iam-policy $PROJECT_ID

# Add user to project
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=user:email@example.com \
  --role=roles/editor

# View audit logs
gcloud logging read --limit 10 --format json

# Enable binary authorization
gcloud container binauthz policy get
```

## 📱 Update Procedures

### Update Backend Code
```bash
# Make code changes, then:
cd backend
docker build -t gcr.io/$PROJECT_ID/rubiscape-backend .
docker push gcr.io/$PROJECT_ID/rubiscape-backend
gcloud run deploy rubiscape-backend \
  --image=gcr.io/$PROJECT_ID/rubiscape-backend \
  --region=$REGION
```

### Update Frontend Code
```bash
cd frontend
npm install
npm run build
gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/
```

### Update Environment Variables
```bash
gcloud run services update rubiscape-backend \
  --set-env-vars="KEY1=value1,KEY2=value2" \
  --region=$REGION
```

## 🌐 Custom Domain Setup

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service=rubiscape-backend \
  --domain=api.yourdomain.com \
  --region=$REGION

# Update DNS to point to load balancer
# Get CNAME with: gcloud run domain-mappings describe api.yourdomain.com

# For frontend (using Cloud CDN), set up load balancer
# Manual task in Cloud Console
```

## 📚 Useful Links

| Resource | URL |
|----------|-----|
| GCP Console | https://console.cloud.google.com |
| Cloud Run Docs | https://cloud.google.com/run/docs |
| Cloud SQL Docs | https://cloud.google.com/sql/docs |
| Cloud Storage Docs | https://cloud.google.com/storage/docs |
| Pricing Calculator | https://cloud.google.com/products/calculator |
| gcloud CLI Docs | https://cloud.google.com/cli/docs |

## 🎯 Useful Environment Variable Setup

```bash
# Set these once, then use throughout
export PROJECT_ID="my-rubiscape-project"
export REGION="us-central1"
export DB_PASSWORD="your-secure-password-123"
export SECRET_KEY="your-secret-key-here-32-chars-minimum"
export DB_IP=$(gcloud sql instances describe rubiscape-db \
  --format='value(ipAddresses[0].ipAddress)')
export BACKEND_URL=$(gcloud run services describe rubiscape-backend \
  --region=$REGION --format='value(status.url)')
export IMAGE_NAME="gcr.io/$PROJECT_ID/rubiscape-backend"
export BUCKET_NAME="gs://$PROJECT_ID-frontend"

# Verify all set correctly
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "DB IP: $DB_IP"
echo "Backend URL: $BACKEND_URL"
echo "Image: $IMAGE_NAME"
echo "Bucket: $BUCKET_NAME"
```

---

**Use this guide for quick lookups while deploying. Refer to CLOUD_SETUP.md or CLOUD_QUICK_START.md for detailed explanations.**
