# Cloud Deployment Quick Start

Complete step-by-step guide to deploy to Google Cloud Platform within 30 minutes.

## ⚡ Quick Prerequisites Check

Before starting, make sure you have:
- [ ] Google Cloud Account (free tier available)
- [ ] `gcloud` CLI installed
- [ ] Docker installed
- [ ] Node.js installed
- [ ] Git installed

## 🚀 Quick Setup (5 minutes)

### 1. Create GCP Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project
export PROJECT_ID=my-rubiscape-$(date +%s)
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudsql.googleapis.com run.googleapis.com storage-api.googleapis.com
```

### 2. Set Environment Variables

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export DB_PASSWORD="your-secure-password-123"
export SECRET_KEY="your-secret-key-here-min-32-chars"
```

### 3. Create Cloud SQL Database (5 minutes)

```bash
# Create PostgreSQL instance
gcloud sql instances create rubiscape-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create rubiscape_ml --instance=rubiscape-db

# Create user
gcloud sql users create postgres --instance=rubiscape-db --password=$DB_PASSWORD

# Get IP address
export DB_IP=$(gcloud sql instances describe rubiscape-db \
  --format='value(ipAddresses[0].ipAddress)')
echo "Database IP: $DB_IP"
```

### 4. Deploy Backend (10 minutes)

```bash
# Configure Docker
gcloud auth configure-docker

# Build and push image
cd backend
docker build -t gcr.io/$PROJECT_ID/rubiscape-backend .
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

# Get backend URL
export BACKEND_URL=$(gcloud run services describe rubiscape-backend \
  --region=$REGION --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"
cd ..
```

### 5. Deploy Frontend (10 minutes)

```bash
# Build frontend
cd frontend
npm install
REACT_APP_API_URL=$BACKEND_URL/api/v1 npm run build

# Upload to Cloud Storage
gsutil mb gs://$PROJECT_ID-frontend
gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/
gsutil web set -m index.html -e index.html gs://$PROJECT_ID-frontend

echo "Frontend URL: https://storage.googleapis.com/$PROJECT_ID-frontend/index.html"
cd ..
```

## ✅ Verification Checklist

After deployment, verify everything works:

```bash
# 1. Check backend health
curl $BACKEND_URL/health

# 2. Check database connectivity
curl $BACKEND_URL/ready

# 3. View backend logs
gcloud run logs read rubiscape-backend --region=$REGION --limit=20

# 4. Test API endpoints
curl $BACKEND_URL/api/v1/

# 5. Check frontend (open in browser)
echo $BACKEND_URL
```

## 🔧 Configuration Files

### Backend Environment Variables

Location: `backend/.env.example`

Key variables:
- `DATABASE_URL` - Cloud SQL connection string
- `SECRET_KEY` - Application secret key
- `ALLOWED_ORIGINS` - Frontend URL for CORS
- `ENVIRONMENT` - Set to "production"
- `LOG_LEVEL` - Set to "info" or "debug"

### Frontend Environment Variables

Location: `frontend/.env.production`

```env
REACT_APP_API_URL=https://your-backend-url.run.app/api/v1
```

## 📊 Cost Management

### Free Tier Coverage

Google Cloud free tier includes:
- **Cloud Run**: 2 million requests/month
- **Cloud SQL**: 30GB storage + 5GB backups
- **Cloud Storage**: 5GB storage

### Estimated Monthly Costs (Beyond Free Tier)

| Service | Tier | Cost |
|---------|------|------|
| Cloud SQL (db-f1-micro) | Small | $15-20 |
| Cloud Run (512MB) | Variable | $10-20 |
| Cloud Storage | 5GB | $0.10 |
| **Total** | | **$25-50** |

**Enable alerts to control costs:**
```bash
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Rubiscape Budget" \
  --budget-amount=50 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=100
```

## 🆘 Troubleshooting

### Backend Won't Start

```bash
# View recent logs
gcloud run logs read rubiscape-backend --region=$REGION --limit=50

# Common issues:
# 1. Database connection - Check DB IP and password
# 2. Environment variables - Verify all required vars are set
# 3. Memory - Try increasing to 1GB (--memory=1Gi)
```

### Frontend Not Loading

```bash
# Check bucket permissions
gsutil ls gs://$PROJECT_ID-frontend

# Check CORS policy
gcloud run services describe rubiscape-backend \
  --region=$REGION \
  --format='value(spec.template.spec.containers[0].env[?name==ALLOWED_ORIGINS].value)'

# View browser console for API errors
```

### Can't Connect to Database

```bash
# Check Cloud SQL instance status
gcloud sql instances describe rubiscape-db

# Verify database user
gcloud sql users list --instance=rubiscape-db

# Check authorized networks
gcloud sql instances describe rubiscape-db \
  --format='value(settings.ipConfiguration.authorizedNetworks[*])'
```

## 📱 Update & Remove Deployment

### Update Backend Code

```bash
# Make code changes, then:
cd backend
docker build -t gcr.io/$PROJECT_ID/rubiscape-backend .
docker push gcr.io/$PROJECT_ID/rubiscape-backend

# Deploy updated version
gcloud run deploy rubiscape-backend \
  --image=gcr.io/$PROJECT_ID/rubiscape-backend \
  --region=$REGION
```

### Update Frontend

```bash
cd frontend
npm run build
gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/
```

### Delete Everything (Cleanup)

```bash
# Delete Cloud Run service
gcloud run services delete rubiscape-backend --region=$REGION

# Delete Cloud SQL instance
gcloud sql instances delete rubiscape-db

# Delete Cloud Storage bucket
gsutil -r rm gs://$PROJECT_ID-frontend

# Delete project (WARNING: Can't undo!)
gcloud projects delete $PROJECT_ID
```

## 🎯 Next Steps

1. ✅ Complete Quick Setup (steps 1-5)
2. ✅ Verify deployment (check verification checklist)
3. 📧 Set up monitoring: See [CLOUD_SETUP.md](CLOUD_SETUP.md#step-9-monitoring--logging)
4. 🔐 Add custom domain: See [CLOUD_SETUP.md](CLOUD_SETUP.md#step-10-domain--ssl-optional)
5. 🛡️ Enable Cloud Armor for DDoS protection
6. 📊 Set up dashboards in Cloud Monitoring

## 📚 Additional Resources

- [Cloud Run Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- [Cloud SQL Guide](https://cloud.google.com/sql/docs/postgres/quickstart)
- [Cloud Storage Guide](https://cloud.google.com/storage/docs/quickstart-gsutil)
- [GCP Console](https://console.cloud.google.com)
- [GCP Pricing](https://cloud.google.com/products/calculator)

## 💡 Pro Tips

1. **Use Cloud Shell** - No setup needed, just use browser-based terminal
2. **Enable billing alerts** - Avoid surprise charges
3. **Use Cloud Monitoring** - Set up dashboards for performance
4. **Enable VPC Service Controls** - Add security layer
5. **Use Cloud KMS** for secrets management instead of plaintext env vars

---

**Estimated Time**: 30 minutes
**Free Tier**: Yes (covers this entire project)
**Next Step**: Run step 1 above!
