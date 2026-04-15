# GitHub Deployment Setup for Rubiscape Repository

Complete step-by-step guide to deploy your Rubiscape project to Google Cloud Platform using GitHub Actions.

---

## 🚀 PHASE 1: Push Code to Rubiscape Repository (5 minutes)

### Step 1: Initialize and push your code

```bash
cd c:\Users\anshb\Desktop\,\industryproject\execution-project

git init
git config user.name "Your Name"
git config user.email "your-email@example.com"

git add .
git commit -m "Initial commit: Rubiscape ML Pipeline Tracker"
git branch -M main

# Add your Rubiscape repository
git remote add origin https://github.com/YOUR_USERNAME/Rubiscape.git

# Push to main branch
git push -u origin main
```

### Step 2: Verify code is on GitHub
- Go to https://github.com/YOUR_USERNAME/Rubiscape
- You should see all your project files

---

## 🔐 PHASE 2: Create GCP Service Account (10 minutes)

### Step 1: Set your GCP Project ID
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

gcloud config set project $PROJECT_ID
```

### Step 2: Create service account for GitHub
```bash
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Deployment Account for Rubiscape"
```

### Step 3: Grant permissions
```bash
# Cloud Run Deploy
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Container Registry (push images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Cloud SQL Client
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Cloud SQL Instance User
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.instanceUser"

# Cloud Build (to build images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"
```

### Step 4: Create and download service account key
```bash
gcloud iam service-accounts keys create github-deploy-key.json \
  --iam-account=github-deployer@$PROJECT_ID.iam.gserviceaccount.com

# Display the contents (you'll need this for GitHub Secrets)
cat github-deploy-key.json
```

**⚠️ IMPORTANT:** Keep `github-deploy-key.json` safe. Don't commit it to GitHub!

---

## 🔐 PHASE 3: Add GitHub Secrets (5 minutes)

### Step 1: Go to GitHub Repository Settings
1. Open https://github.com/YOUR_USERNAME/Rubiscape
2. Click **Settings** tab
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Step 2: Add these 6 secrets one by one

#### Secret 1: GCP_PROJECT_ID
- **Name:** `GCP_PROJECT_ID`
- **Value:** Your GCP project ID (e.g., `my-project-123`)

#### Secret 2: GCP_SERVICE_ACCOUNT_JSON
- **Name:** `GCP_SERVICE_ACCOUNT_JSON`
- **Value:** Entire contents of `github-deploy-key.json` file (copy the full JSON)

#### Secret 3: DB_PASSWORD
- **Name:** `DB_PASSWORD`
- **Value:** Your Cloud SQL password (min 8 characters, use strong password)

#### Secret 4: SECRET_KEY
- **Name:** `SECRET_KEY`
- **Value:** Strong secret key (min 32 characters) - use something like: `your-random-secret-key-with-32-chars-minimum!!!`

#### Secret 5: DATABASE_IP
- **Name:** `DATABASE_IP`
- **Value:** Your Cloud SQL public IP address (e.g., `35.192.123.456`)

#### Secret 6: REGION
- **Name:** `REGION`
- **Value:** `us-central1`

**How to add each secret:**
1. Click "New repository secret"
2. Enter Name
3. Enter Value
4. Click "Add secret"
5. Repeat for next secret

---

## 🗄️ PHASE 4: Set Up Cloud SQL Database (10 minutes)

### Step 1: Create PostgreSQL instance
```bash
gcloud sql instances create rubiscape-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --authorized-networks=0.0.0.0/0
```

Wait 5-10 minutes for creation...

### Step 2: Create database and user
```bash
# Create database
gcloud sql databases create rubiscape_ml --instance=rubiscape-db

# Create user
gcloud sql users create postgres --instance=rubiscape-db \
  --password=YOUR_DB_PASSWORD
```

Replace `YOUR_DB_PASSWORD` with your DB_PASSWORD secret value!

### Step 3: Get the database IP
```bash
gcloud sql instances describe rubiscape-db \
  --format='value(ipAddresses[0].ipAddress)'
```

Copy this IP and use it as your `DATABASE_IP` secret in GitHub!

---

## 🎯 PHASE 5: Test Deployment (5 minutes)

### Step 1: Push a commit to trigger deployment
```bash
cd c:\Users\anshb\Desktop\,\industryproject\execution-project

# Make a small change (e.g., update README)
echo "## Deployed via GitHub Actions" >> README.md

git add README.md
git commit -m "Trigger automatic deployment"
git push origin main
```

### Step 2: Watch deployment in GitHub
1. Go to https://github.com/YOUR_USERNAME/Rubiscape
2. Click **Actions** tab
3. Click the running workflow "Deploy to GCP"
4. Watch logs in real-time
5. Wait for completion (~15 minutes)

### Step 3: Verify deployment
```bash
# Check backend deployed
gcloud run services describe rubiscape-backend --region=us-central1

# Check frontend files
gsutil ls gs://YOUR_PROJECT_ID-frontend/

# Test backend health
curl https://rubiscape-backend-xxx.run.app/health
```

---

## 📊 How Deployment Works

### Automatic Deployment (On Every Push to main)
```
You push code to GitHub
    ↓
GitHub Actions triggered automatically
    ↓
Tests run (backend & frontend)
    ↓
Backend Docker image built
    ↓
Image pushed to Google Container Registry
    ↓
Backend deployed to Cloud Run
    ↓
Frontend built with backend URL
    ↓
Frontend uploaded to Cloud Storage
    ↓
✅ Live at:
   - Backend: https://rubiscape-backend-xxx.run.app
   - Frontend: https://storage.googleapis.com/YOUR_PROJECT_ID-frontend/
```

---

## 🎯 Three Ways to Deploy

### Option 1: Automatic (Recommended)
- Every time you push to `main` branch
- Workflow automatically triggers
- Takes ~15 minutes

```bash
git push origin main
# Deployment starts automatically
```

### Option 2: Manual Trigger from GitHub UI
1. Go to repo → **Actions** tab
2. Select **"Manual Deploy to GCP"** workflow
3. Click **"Run workflow"** button
4. Select environment: `production`
5. Click **"Run workflow"**

### Option 3: Pull Request Preview
Create a pull request → Tests run automatically → Shows pass/fail status

---

## 📝 Current Workflow Files

Your repository now has 3 GitHub Actions workflows:

### `.github/workflows/deploy.yml`
- **Triggers:** Every push to `main`
- **Actions:** Build, test, deploy everything
- **Time:** ~15 minutes

### `.github/workflows/ci.yml`
- **Triggers:** Every push, all pull requests
- **Actions:** Run tests, linting, build validation
- **Time:** ~5-8 minutes

### `.github/workflows/manual-deploy.yml`
- **Triggers:** Manual (workflow_dispatch)
- **Actions:** Deploy to selected environment
- **Time:** ~15 minutes

---

## 🔍 Monitor Your Deployment

### View GitHub Actions Logs
1. Go to https://github.com/YOUR_USERNAME/Rubiscape/actions
2. Click on workflow run
3. Click on job to see detailed logs
4. Search for errors/issues

### View GCP Logs
```bash
# Backend logs
gcloud run logs read rubiscape-backend --region=us-central1 --limit=50

# See recent backend activity
gcloud run logs read rubiscape-backend --region=us-central1 --limit=100 | grep -i "error\|connection"

# See deployed images
gcloud container images list --project=$PROJECT_ID

# See frontend files
gsutil ls -r gs://YOUR_PROJECT_ID-frontend/
```

### Test Your Deployed App
```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe rubiscape-backend \
  --region=us-central1 --format='value(status.url)')

# Test health
curl $BACKEND_URL/health

# Test in browser
echo "Frontend: https://storage.googleapis.com/YOUR_PROJECT_ID-frontend/"
echo "Backend: $BACKEND_URL"
```

---

## 🐛 Troubleshooting

### "Deployment Failed: Authentication Error"
**Solution:**
```bash
# Verify service account was created
gcloud iam service-accounts list

# Verify key was created
gcloud iam service-accounts keys list \
  --iam-account=github-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

### "Database Connection Refused"
**Solution:**
```bash
# Check Cloud SQL instance exists
gcloud sql instances list

# Verify it's running
gcloud sql instances describe rubiscape-db --format='value(state)'

# Check authorized networks
gcloud sql instances describe rubiscape-db \
  --format='value(settings.ipConfiguration.authorizedNetworks[*].value)'
```

### "Frontend Not Updating"
**Solution:**
```bash
# Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
# OR manually clear Cloud Storage

gsutil rm -r gs://YOUR_PROJECT_ID-frontend/*
git push origin main  # Re-deploy
```

### "Tests Failing in GitHub"
- Click the failed workflow in Actions
- Read the error log carefully
- Fix the issue locally
- Push again to retry

---

## ✅ Checklist: Complete Setup Verification

Before your first production deployment, verify:

- [ ] Code pushed to https://github.com/YOUR_USERNAME/Rubiscape
- [ ] All 6 GitHub Secrets added correctly
  - [ ] GCP_PROJECT_ID
  - [ ] GCP_SERVICE_ACCOUNT_JSON
  - [ ] DB_PASSWORD
  - [ ] SECRET_KEY
  - [ ] DATABASE_IP
  - [ ] REGION
- [ ] Cloud SQL instance created and running
- [ ] Cloud SQL database `rubiscape_ml` created
- [ ] Cloud SQL user `postgres` created
- [ ] Service account `github-deployer` exists
- [ ] Service account has all 5 required roles
- [ ] First deployment completed successfully
- [ ] Backend responds to health check
- [ ] Frontend loads in browser
- [ ] Can log in and use the app
- [ ] Logs show no errors

---

## 🚀 Quick Start Summary

**For Rubiscape repository deployment:**

1. **Push code:**
   ```bash
   cd execution-project
   git add .
   git commit -m "Deploy to Rubiscape repo"
   git push origin main
   ```

2. **Add GitHub secrets:** (6 secrets in Settings → Secrets)

3. **Create GCP service account:**
   ```bash
   gcloud iam service-accounts create github-deployer
   # Run all role assignments (see PHASE 2 above)
   gcloud iam service-accounts keys create github-deploy-key.json \
     --iam-account=github-deployer@$PROJECT_ID.iam.gserviceaccount.com
   ```

4. **Create Cloud SQL database:**
   ```bash
   gcloud sql instances create rubiscape-db --database-version=POSTGRES_15 --tier=db-f1-micro
   gcloud sql databases create rubiscape_ml --instance=rubiscape-db
   ```

5. **Get DATABASE_IP and add to secrets:**
   ```bash
   gcloud sql instances describe rubiscape-db --format='value(ipAddresses[0].ipAddress)'
   ```

6. **Push code to trigger deployment:**
   ```bash
   git push origin main
   # Watch at: github.com/YOUR_USERNAME/Rubiscape/actions
   ```

7. **Access your app:**
   - Frontend: `https://storage.googleapis.com/YOUR_PROJECT_ID-frontend/`
   - Backend: `https://rubiscape-backend-xxx.run.app`

---

## 🎓 Next Steps

1. Complete all 5 phases above
2. Make your first push to `main`
3. Watch deployment in Actions tab
4. Test the live application
5. Share URLs with your team
6. Make future changes → Push → Auto-deploy!

For detailed information, see [CLOUD_SETUP.md](./CLOUD_SETUP.md)
