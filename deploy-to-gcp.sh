#!/bin/bash
# Google Cloud Platform Deployment Script
# This script automates the deployment of Rubiscape ML Pipeline Tracker to GCP

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-my-rubiscape-project}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="rubiscape-backend"
DB_INSTANCE="rubiscape-db"
DB_NAME="rubiscape_ml"
DB_USER="postgres"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}GCP Deployment Script${NC}"
echo -e "${YELLOW}========================================${NC}"

# Step 1: Authentication
echo -e "\n${YELLOW}Step 1: Authenticating with GCP...${NC}"
gcloud auth login

# Step 2: Set project
echo -e "\n${YELLOW}Step 2: Setting up project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}"

# Step 3: Enable APIs
echo -e "\n${YELLOW}Step 3: Enabling required GCP APIs...${NC}"
gcloud services enable \
  cloudsql.googleapis.com \
  sqladmin.googleapis.com \
  run.googleapis.com \
  storage-api.googleapis.com \
  compute.googleapis.com \
  containerregistry.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}"

# Step 4: Check if Cloud SQL instance exists
echo -e "\n${YELLOW}Step 4: Setting up Cloud SQL...${NC}"
if gcloud sql instances describe $DB_INSTANCE --quiet 2>/dev/null; then
  echo -e "${GREEN}✓ Cloud SQL instance already exists${NC}"
else
  echo -e "${YELLOW}Creating Cloud SQL instance (this may take 5-10 minutes)...${NC}"
  gcloud sql instances create $DB_INSTANCE \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --authorized-networks=0.0.0.0/0 \
    --backup-start-time=03:00 \
    --enable-bin-log
  echo -e "${GREEN}✓ Cloud SQL instance created${NC}"
fi

# Step 5: Create database
echo -e "\n${YELLOW}Step 5: Creating database...${NC}"
if gcloud sql databases describe $DB_NAME --instance=$DB_INSTANCE --quiet 2>/dev/null; then
  echo -e "${GREEN}✓ Database already exists${NC}"
else
  gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
  echo -e "${GREEN}✓ Database created${NC}"
fi

# Step 6: Get Cloud SQL IP
echo -e "\n${YELLOW}Step 6: Getting Cloud SQL connection details...${NC}"
DB_IP=$(gcloud sql instances describe $DB_INSTANCE --format='value(ipAddresses[0].ipAddress)')
echo -e "${GREEN}✓ Cloud SQL IP: $DB_IP${NC}"

# Step 7: Build and push Docker image
echo -e "\n${YELLOW}Step 7: Building and pushing Docker image...${NC}"
gcloud auth configure-docker

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
cd backend
docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME
echo -e "${GREEN}✓ Docker image pushed: $IMAGE_NAME${NC}"
cd ..

# Step 8: Deploy to Cloud Run
echo -e "\n${YELLOW}Step 8: Deploying to Cloud Run...${NC}"
read -p "Enter database password: " DB_PASSWORD
read -p "Enter secret key: " SECRET_KEY

gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600 \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_IP:5432/$DB_NAME,SECRET_KEY=$SECRET_KEY,ENVIRONMENT=production"

echo -e "${GREEN}✓ Backend deployed to Cloud Run${NC}"

# Step 9: Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo -e "${GREEN}✓ Backend URL: $BACKEND_URL${NC}"

# Step 10: Build frontend
echo -e "\n${YELLOW}Step 9: Building frontend...${NC}"
cd frontend
npm install
REACT_APP_API_URL=$BACKEND_URL/api/v1 npm run build
echo -e "${GREEN}✓ Frontend built${NC}"
cd ..

# Step 11: Deploy frontend to Cloud Storage
echo -e "\n${YELLOW}Step 10: Deploying frontend to Cloud Storage...${NC}"
BUCKET_NAME="gs://$PROJECT_ID-frontend"
gsutil mb $BUCKET_NAME || echo "Bucket already exists"
gsutil -m cp -r frontend/build/* $BUCKET_NAME/
gsutil web set -m index.html -e index.html $BUCKET_NAME

echo -e "${GREEN}✓ Frontend deployed${NC}"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Backend URL:${NC} $BACKEND_URL"
echo -e "${YELLOW}Frontend URL:${NC} https://storage.googleapis.com/$PROJECT_ID-frontend/index.html"
echo -e "${YELLOW}Cloud SQL IP:${NC} $DB_IP"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update frontend environment variables if needed"
echo "2. Test the application"
echo "3. Set up monitoring in Cloud Console"
echo "4. Configure custom domain (optional)"
