# Cloud Deployment Checklist

Complete checklist for deploying Rubiscape ML Pipeline Tracker to Google Cloud Platform.

## 📋 Pre-Deployment

- [ ] Google Cloud Account created
- [ ] Billing enabled on GCP account
- [ ] Local `gcloud` CLI installed and configured
  ```bash
  gcloud --version
  gcloud auth login
  ```
- [ ] Docker installed and running
  ```bash
  docker --version
  ```
- [ ] Node.js 18+ installed
  ```bash
  node --version
  npm --version
  ```
- [ ] Git installed
  ```bash
  git --version
  ```
- [ ] Backend and frontend work locally
  ```bash
  # Test backend
  cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --reload
  
  # Test frontend
  cd frontend && npm install && npm start
  ```

## 🏗️ GCP Project Setup (Step 1)

- [ ] Create GCP project
  ```bash
  gcloud projects create $PROJECT_ID
  gcloud config set project $PROJECT_ID
  ```
- [ ] Enable required APIs
  ```bash
  gcloud services enable cloudsql.googleapis.com run.googleapis.com storage-api.googleapis.com
  ```
- [ ] Set environment variables
  ```bash
  export PROJECT_ID="your-project-id"
  export REGION="us-central1"
  export DB_PASSWORD="your-secure-password"
  export SECRET_KEY="your-secret-key-32-chars-minimum"
  ```
- [ ] Verify project is active
  ```bash
  gcloud config list
  ```

## 🗄️ Cloud SQL Setup (Step 2)

- [ ] Create PostgreSQL instance
  ```bash
  gcloud sql instances create rubiscape-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION
  ```
  ⏰ Wait 5-10 minutes for instance creation
  
- [ ] Create database
  ```bash
  gcloud sql databases create rubiscape_ml --instance=rubiscape-db
  ```
  
- [ ] Create database user
  ```bash
  gcloud sql users create postgres --instance=rubiscape-db --password=$DB_PASSWORD
  ```
  
- [ ] Get Cloud SQL IP
  ```bash
  export DB_IP=$(gcloud sql instances describe rubiscape-db \
    --format='value(ipAddresses[0].ipAddress)')
  echo $DB_IP
  ```
  
- [ ] Verify database connectivity (from Cloud Shell)
  ```bash
  gcloud sql connect rubiscape-db --user=postgres
  # Enter password when prompted
  # Run: SELECT 1;
  # Exit with: \q
  ```

## 🚀 Backend Deployment (Step 3)

- [ ] Configure Docker authentication
  ```bash
  gcloud auth configure-docker
  ```
  
- [ ] Update backend environment variables in code review
  - [ ] Check `backend/.env.example` has correct structure
  - [ ] Verify `DATABASE_URL` format
  - [ ] Verify `SECRET_KEY` is strong
  
- [ ] Build Docker image
  ```bash
  cd backend
  docker build -t gcr.io/$PROJECT_ID/rubiscape-backend .
  cd ..
  ```
  ✅ Verify build completes without errors
  
- [ ] Push Docker image to Google Container Registry
  ```bash
  docker push gcr.io/$PROJECT_ID/rubiscape-backend
  ```
  ✅ Verify image is in GCR:
  ```bash
  gcloud container images list
  ```
  
- [ ] Deploy to Cloud Run
  ```bash
  gcloud run deploy rubiscape-backend \
    --image=gcr.io/$PROJECT_ID/rubiscape-backend \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8000 \
    --memory=512Mi \
    --cpu=1 \
    --timeout=3600 \
    --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:$DB_PASSWORD@$DB_IP:5432/rubiscape_ml,SECRET_KEY=$SECRET_KEY,ENVIRONMENT=production"
  ```
  ⏰ Wait 5 minutes for deployment
  
- [ ] Get backend URL
  ```bash
  export BACKEND_URL=$(gcloud run services describe rubiscape-backend \
    --region=$REGION --format='value(status.url)')
  echo $BACKEND_URL
  ```
  Save this URL!
  
- [ ] Test backend health
  ```bash
  curl $BACKEND_URL/health
  ```
  ✅ Should return: `{"status":"ok","service":"Rubiscape ML Pipeline Tracker","environment":"production"}`
  
- [ ] Test backend readiness
  ```bash
  curl $BACKEND_URL/ready
  ```
  ✅ Should return: `{"ready":true}`
  
- [ ] Check backend logs
  ```bash
  gcloud run logs read rubiscape-backend --region=$REGION --limit=20
  ```
  ✅ Verify no errors

## 🎨 Frontend Deployment (Step 4)

- [ ] Update frontend environment
  ```bash
  cd frontend
  # Create .env.production file or set env var
  export REACT_APP_API_URL=$BACKEND_URL/api/v1
  ```
  
- [ ] Install dependencies
  ```bash
  npm install
  ```
  ✅ No errors
  
- [ ] Build production bundle
  ```bash
  npm run build
  ```
  ✅ Build succeeds, check `frontend/build/` directory exists
  
- [ ] Create Cloud Storage bucket
  ```bash
  gsutil mb gs://$PROJECT_ID-frontend
  ```
  ✅ Bucket created
  
- [ ] Upload build files
  ```bash
  gsutil -m cp -r build/* gs://$PROJECT_ID-frontend/
  ```
  ✅ Files uploaded
  
- [ ] Verify files uploaded
  ```bash
  gsutil ls gs://$PROJECT_ID-frontend
  ```
  ✅ See index.html and other files
  
- [ ] Configure static website hosting
  ```bash
  gsutil web set -m index.html -e index.html gs://$PROJECT_ID-frontend
  ```
  
- [ ] Get frontend URL
  ```bash
  echo "https://storage.googleapis.com/$PROJECT_ID-frontend/index.html"
  ```
  Save this URL!
  
- [ ] Test frontend loads
  - [ ] Open URL in browser
  - [ ] Check page loads
  - [ ] Open browser console (F12)
  - [ ] Check for errors
  
- [ ] Go back to project directory
  ```bash
  cd ..
  ```

## 🔗 Enable CORS (Step 5)

- [ ] Update backend CORS settings
  ```bash
  gcloud run services update rubiscape-backend \
    --set-env-vars="ALLOWED_ORIGINS=https://storage.googleapis.com/$PROJECT_ID-frontend" \
    --region=$REGION
  ```
  
- [ ] Wait 30 seconds for update
  
- [ ] Test API call from frontend
  - [ ] Open frontend URL
  - [ ] Check browser network tab
  - [ ] Verify CORS headers are correct
  - [ ] **No CORS errors in console**

## 🔐 Security Configuration (Step 6)

- [ ] Store secrets securely
  - [ ] ❌ Do NOT commit `.env` files
  - [ ] ✅ Use `backend/.env.example` for reference
  - [ ] Consider using Google Secret Manager for production
  
- [ ] Configure Cloud SQL authentication
  - [ ] Enable automatic backups
    ```bash
    gcloud sql backups describe
    ```
  - [ ] Review automated backup settings
  
- [ ] Set up VPC (optional, for high security)
  ```bash
  # Advanced topic - see CLOUD_SETUP.md for details
  ```

## 📊 Monitoring & Logging (Step 7)

- [ ] View application logs
  ```bash
  gcloud run logs read rubiscape-backend --limit=50 --region=$REGION
  ```
  
- [ ] Set up Cloud Monitoring dashboard
  - [ ] Go to [Cloud Monitoring Console](https://console.cloud.google.com/monitoring)
  - [ ] Create new dashboard
  - [ ] Add metrics for:
    - [ ] Cloud Run: Request count
    - [ ] Cloud Run: Error rate
    - [ ] Cloud SQL: CPU utilization
    - [ ] Cloud SQL: Connections
  
- [ ] Create alerting policy
  - [ ] Set alert for high error rate (>5%)
  - [ ] Set alert for high CPU (>80%)
  - [ ] Set alert for Cloud SQL connection failures
  
- [ ] Check quotas and limits
  ```bash
  gcloud compute project-info describe --project=$PROJECT_ID
  ```

## ✅ Post-Deployment Verification

- [ ] Backend is running
  ```bash
  gcloud run services describe rubiscape-backend --region=$REGION
  ```
  ✅ Status: Active
  
- [ ] Frontend is accessible
  - [ ] Open frontend URL in browser
  - [ ] Page loads without errors
  - [ ] Can interact with UI
  
- [ ] API communication works
  - [ ] Login works (if applicable)
  - [ ] Can make API requests from frontend
  - [ ] Data loads correctly
  
- [ ] Database is working
  ```bash
  curl $BACKEND_URL/ready
  ```
  ✅ Returns `{"ready":true}`
  
- [ ] Health checks pass
  ```bash
  curl $BACKEND_URL/health
  ```
  ✅ Returns healthy status
  
- [ ] No critical errors in logs
  ```bash
  gcloud run logs read rubiscape-backend --region=$REGION --limit=100 | grep -i error
  ```
  ✅ Only expected warnings (if any)

## 🎬 Production Tasks

- [ ] Set up CDN for static files (optional)
  - [ ] Enable Cloud CDN on Load Balancer
  - [ ] See CLOUD_SETUP.md Step 5.4
  
- [ ] Configure custom domain (optional)
  - [ ] Register domain
  - [ ] Point DNS to Cloud Run
  - [ ] See CLOUD_SETUP.md Step 10
  
- [ ] Set up billing alerts
  ```bash
  # Prevent surprise charges
  ```
  
- [ ] Schedule regular backups
  ```bash
  gcloud sql backups list --instance=rubiscape-db
  ```
  
- [ ] Document deployment details
  - [ ] Backend URL: $BACKEND_URL
  - [ ] Frontend URL: https://storage.googleapis.com/$PROJECT_ID-frontend
  - [ ] Database: rubiscape-db in $REGION
  - [ ] Project ID: $PROJECT_ID
  
- [ ] Share access with team
  - [ ] Add team members to GCP project
  - [ ] Grant appropriate IAM roles
  - [ ] Share documentation

## 📝 Documentation

- [ ] Update README with cloud URLs
- [ ] Document any custom configurations
- [ ] Create runbook for common tasks:
  - [ ] How to view logs
  - [ ] How to scale up
  - [ ] How to rollback
  - [ ] How to add new features

## 🚨 Troubleshooting Checklist

If deployment fails, check:

- [ ] All APIs are enabled
  ```bash
  gcloud services list --enabled
  ```
  
- [ ] Docker image built successfully
  ```bash
  docker images | grep rubiscape-backend
  ```
  
- [ ] Image in Google Container Registry
  ```bash
  gcloud container images list
  ```
  
- [ ] Cloud Run service exists
  ```bash
  gcloud run services list --region=$REGION
  ```
  
- [ ] No quota exceeded errors
  ```bash
  gcloud compute project-info describe --project=$PROJECT_ID | grep QUOTA
  ```
  
- [ ] Cloud SQL instance running
  ```bash
  gcloud sql instances describe rubiscape-db --format='value(state)'
  ```
  
- [ ] Database and user created
  ```bash
  gcloud sql databases list --instance=rubiscape-db
  gcloud sql users list --instance=rubiscape-db
  ```
  
- [ ] Cloud Storage bucket exists
  ```bash
  gsutil ls
  ```

## 🎉 Completion

- [ ] All steps completed
- [ ] Application tested and working
- [ ] Team notified of deployment
- [ ] Documentation updated
- [ ] Monitoring configured
- [ ] Backups scheduled

**Deployment Date**: _______________
**Deployed By**: _______________
**Notes**: _______________

---

**Next**: Monitor the application in production. See CLOUD_SETUP.md for advanced configurations.
