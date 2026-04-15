@REM Google Cloud Platform Deployment Script (Windows)
@REM This script automates the deployment to GCP

@echo off
setlocal enabledelayedexpansion

REM Configuration
set PROJECT_ID=%GCP_PROJECT_ID%
if "%PROJECT_ID%"=="" set PROJECT_ID=my-rubiscape-project

set REGION=%GCP_REGION%
if "%REGION%"=="" set REGION=us-central1

set SERVICE_NAME=rubiscape-backend
set DB_INSTANCE=rubiscape-db
set DB_NAME=rubiscape_ml
set DB_USER=postgres

echo.
echo ========================================
echo GCP Deployment Script (Windows)
echo ========================================
echo.

REM Step 1: Authentication
echo Step 1: Authenticating with GCP...
call gcloud auth login

REM Step 2: Set project
echo.
echo Step 2: Setting up project...
call gcloud config set project %PROJECT_ID%
echo Project set to: %PROJECT_ID%

REM Step 3: Enable APIs
echo.
echo Step 3: Enabling required GCP APIs...
call gcloud services enable ^
  cloudsql.googleapis.com ^
  sqladmin.googleapis.com ^
  run.googleapis.com ^
  storage-api.googleapis.com ^
  compute.googleapis.com ^
  containerregistry.googleapis.com

echo APIs enabled

REM Step 4: Configure Docker
echo.
echo Step 4: Configuring Docker for GCP...
call gcloud auth configure-docker

REM Step 5: Build and push Docker image
echo.
echo Step 5: Building and pushing Docker image...
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%
cd backend
call docker build -t %IMAGE_NAME% .
call docker push %IMAGE_NAME%
cd ..
echo Docker image built and pushed: %IMAGE_NAME%

REM Step 6: Deploy to Cloud Run
echo.
echo Step 6: Deploying to Cloud Run...
echo Please enter the following credentials:
set /p DB_PASSWORD="Database password: "
set /p SECRET_KEY="Secret key: "

call gcloud run deploy %SERVICE_NAME% ^
  --image=%IMAGE_NAME% ^
  --platform=managed ^
  --region=%REGION% ^
  --allow-unauthenticated ^
  --port=8000 ^
  --memory=512Mi ^
  --cpu=1 ^
  --timeout=3600

echo Backend deployed to Cloud Run

REM Step 7: Get backend URL
echo.
echo Retrieving backend URL...
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set BACKEND_URL=%%i
echo Backend URL: %BACKEND_URL%

REM Step 8: Build frontend
echo.
echo Step 7: Building frontend...
cd frontend
call npm install
set REACT_APP_API_URL=%BACKEND_URL%/api/v1
call npm run build
cd ..
echo Frontend built

REM Step 9: Deploy to Cloud Storage
echo.
echo Step 8: Deploying frontend to Cloud Storage...
set BUCKET_NAME=gs://%PROJECT_ID%-frontend
call gsutil mb %BUCKET_NAME%
call gsutil -m cp -r frontend/build/* %BUCKET_NAME%/
call gsutil web set -m index.html -e index.html %BUCKET_NAME%

echo Frontend deployed

REM Summary
echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo Backend URL: %BACKEND_URL%
echo Frontend URL: https://storage.googleapis.com/%PROJECT_ID%-frontend/index.html
echo.
echo Next steps:
echo 1. Test the application
echo 2. Set up monitoring in Cloud Console
echo 3. Configure custom domain (optional)

pause
