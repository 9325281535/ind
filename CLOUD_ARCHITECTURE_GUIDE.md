# Cloud Deployment Flow & Architecture Guide

Visual guide to understand the cloud setup and deployment flow.

## 🏗️ System Architecture

### Before (Local Development)
```
Developer's Machine
┌─────────────────────────────────┐
│  Desktop/Laptop                  │
│  ┌──────────────────────────┐   │
│  │  React (Port 3000)       │   │
│  │  ├─ npm start            │   │
│  │  └─ localhost:3000       │   │
│  └──────────────────────────┘   │
│           │ HTTP                │
│           ▼                      │
│  ┌──────────────────────────┐   │
│  │  FastAPI (Port 8000)     │   │
│  │  ├─ python -m uvicorn    │   │
│  │  └─ localhost:8000       │   │
│  └──────────────────────────┘   │
│           │ SQL                 │
│           ▼                      │
│  ┌──────────────────────────┐   │
│  │  PostgreSQL (Port 5432)  │   │
│  │  ├─ docker-compose       │   │
│  │  └─ localhost:5432       │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

### After (Google Cloud)
```
                   Internet
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌─────────┐   ┌─────────┐   ┌──────────┐
    │ Browser │   │   API   │   │ Storage  │
    │ Users   │   │ Clients │   │ Services │
    └────┬────┘   └────┬────┘   └────┬─────┘
         │             │             │
    Cloud CDN ◄────────┼─────────────┘
         │             │
         │   HTTPS/SSL │
         │ (Automatic) │
         ▼             ▼
    ┌──────────────────────────┐
    │   Google Cloud           │
    │  ┌────────────────────┐  │
    │  │ Cloud Storage      │  │
    │  │ React Build Files  │  │
    │  │ + CDN (Optional)   │  │
    │  └────────────────────┘  │
    │           │              │
    │           │ HTTP/JSON    │
    │           ▼              │
    │  ┌────────────────────┐  │
    │  │ Cloud Run          │  │
    │  │ FastAPI Backend    │  │
    │  │ Port: 8000         │  │
    │  │ Memory: 512MB      │  │
    │  │ Auto-scaling       │  │
    │  └────────────────────┘  │
    │           │              │
    │           │ SQL/TCP      │
    │           ▼              │
    │  ┌────────────────────┐  │
    │  │ Cloud SQL          │  │
    │  │ PostgreSQL 15      │  │
    │  │ Instance: micro    │  │
    │  │ Managed/Secure     │  │
    │  └────────────────────┘  │
    │                          │
    └──────────────────────────┘
```

## 📋 Deployment Process Flow

### Step 1: Preparation (5 min)
```
┌─────────────────┐
│ Check Local    │
│ Setup Works    │◄─── Test backend & frontend locally
└────────┬────────┘
         │
         ▼
   ✅ Ready
```

### Step 2: GCP Project Setup (5 min)
```
┌──────────────────────┐
│ Create GCP Project  │
├──────────────────────┤
│ 1. Create project   │
│ 2. Set billing      │
│ 3. Enable APIs      │
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│ Auth Configured     │
└────────┬────────────┘
         │
         ▼
   ✅ Ready
```

### Step 3: Database Setup (10 min)
```
┌──────────────────────────┐
│ Create Cloud SQL        │
├──────────────────────────┤
│ 1. PostgreSQL Instance  │
│ 2. Create Database      │
│ 3. Create User          │
│ 4. Get IP Address       │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Database Ready          │
│ postgres@IP:5432        │
└────────┬────────────────┘
         │
         ▼
   ✅ Ready
```

### Step 4: Backend Deployment (15 min)
```
┌──────────────────────────┐
│ Build Docker Image      │
├──────────────────────────┤
│ backend/Dockerfile      │
│ + requirements.txt      │
│ = Docker Image          │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Push to GCR             │
├──────────────────────────┤
│ gcr.io/PROJECT/service  │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Deploy to Cloud Run     │
├──────────────────────────┤
│ Configure:              │
│ - Memory: 512MB         │
│ - Port: 8000            │
│ - Env vars              │
│ - DATABASE_URL ──────┐  │
│ - SECRET_KEY          │  │
│ - ENVIRONMENT         │  │
└────────┬───────────────┘  │
         │                  │
         ▼                  │
┌──────────────────────────┐│
│ Cloud Run Service       ││
│ Status: Active          ││
│ URL: backend.run.app    │◄┘
└────────┬────────────────┘
         │
         ▼
   ✅ Ready
```

### Step 5: Frontend Deployment (15 min)
```
┌──────────────────────────┐
│ Build React App         │
├──────────────────────────┤
│ npm install             │
│ npm run build           │
│ = build/ folder         │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Upload to Cloud Storage │
├──────────────────────────┤
│ gsutil cp build/* gs://  │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Configure Static Website│
├──────────────────────────┤
│ Index: index.html       │
│ Error: index.html       │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Cloud Storage Bucket    │
│ Status: Active          │
│ URL: storage.cloud.com  │
└────────┬────────────────┘
         │
         ▼
   ✅ Ready
```

### Step 6: Configuration (5 min)
```
┌──────────────────────────┐
│ Update CORS Settings    │
├──────────────────────────┤
│ Add frontend URL        │
│ to allowed origins      │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Health Checks Enabled   │
├──────────────────────────┤
│ /health - liveness      │
│ /ready - startup        │
└────────┬────────────────┘
         │
         ▼
   ✅ Ready
```

### Step 7: Testing (5 min)
```
┌──────────────────────────┐
│ Test Backend            │
├──────────────────────────┤
│ curl backend-url/health │
│ curl backend-url/ready  │
└────────┬────────────────┘
         │
    ✅ OK│
         │
         ▼
┌──────────────────────────┐
│ Test Frontend           │
├──────────────────────────┤
│ Open in browser         │
│ Check console           │
└────────┬────────────────┘
         │
    ✅ OK│
         │
         ▼
┌──────────────────────────┐
│ Test API Connection     │
├──────────────────────────┤
│ Login / API calls       │
│ from frontend           │
└────────┬────────────────┘
         │
    ✅ OK│
         │
         ▼
    🎉 LIVE!
```

## 🔄 Request Flow (After Deployment)

### User opens frontend
```
1. Browser makes request
   ├─ URL: https://storage.googleapis.com/bucket/index.html
   │
   └─► Cloud CDN (optional caching)
       │
       └─► Cloud Storage
           └─► index.html, JS, CSS files
               │
               ├─ Loads React app
               │
               └─ React app loads data from API

2. React app needs data
   ├─ Makes API call
   │
   ├─ URL: https://backend-url.run.app/api/v1/...
   │
   └─► Internet → Cloud Run
       │
       ├─ FastAPI processes request
       │
       └─ Queries Cloud SQL
           │
           └─ PostgreSQL returns data
               │
               └─ FastAPI returns JSON to frontend

3. Frontend displays data
   ├─ React renders
   │
   └─► User sees live application!
```

## 🚀 Deployment Decision Tree

```
Start
  │
  ├─ Want to learn everything?
  │  └─► Read CLOUD_SETUP.md (detailed guide)
  │
  ├─ Want to deploy quickly?
  │  └─► Follow CLOUD_QUICK_START.md (30 min)
  │
  ├─ Want to track progress?
  │  └─► Use CLOUD_DEPLOYMENT_CHECKLIST.md
  │
  ├─ Want automation?
  │  └─► Run deploy-to-gcp.sh or .bat
  │
  └─ Need quick reference?
     └─► Use CLOUD_QUICK_REFERENCE.md

After choosing:
  │
  ├─ Set up GCP project
  │
  ├─ Create Cloud SQL
  │
  ├─ Deploy backend
  │
  ├─ Deploy frontend
  │
  ├─ Test everything
  │
  └─► 🎉 IN PRODUCTION!
```

## 📊 Time Estimation

| Step | Task | Time | Waiting | Total |
|------|------|------|---------|-------|
| 1 | Local setup check | 5 min | - | 5 min |
| 2 | GCP project | 5 min | - | 10 min |
| 3 | Cloud SQL | 5 min | 5-10 min | 20-25 min |
| 4 | Backend build | 5 min | 5-10 min | 30-40 min |
| 5 | Frontend build | 10 min | 5 min | 45-55 min |
| 6 | Configuration | 5 min | - | 50-60 min |
| 7 | Testing | 5 min | - | 55-65 min |

**Total: 55-65 minutes (mostly waiting for cloud provisioning)**

## 🔐 Security Flow

### Data Flow Security
```
User's Browser
        │
        │ HTTPS (SSL/TLS - Automatic)
        │ 🔒 Encrypted
        │
        ▼
Cloud Run Service
        │
        │ Private network
        │ (VPC - Optional)
        │
        ▼
Cloud SQL Database
        │
        │ 🔐 Encrypted at rest
        │ 🔒 Password protected
        │ 🛡️ Firewall rules
        │
        ▼
PostgreSQL Server
```

### Secrets Management
```
Before: ❌
DATABASE_URL=postgresql://user:PASSWORD@host:5432/db
↓
After: ✅
Database URL stored in:
- Cloud Run environment variables (encrypted)
- Or Google Secret Manager (recommended for production)
```

## 🆘 Troubleshooting Flow

```
Something not working?
│
├─ Frontend not loading?
│  ├─ Check Cloud Storage bucket
│  ├─ Verify files uploaded
│  └─ Check browser console
│
├─ API errors?
│  ├─ Check Cloud Run logs
│  ├─ Verify CORS settings
│  └─ Check backend health
│
├─ Database connection error?
│  ├─ Check Cloud SQL IP
│  ├─ Verify password
│  └─ Check firewall rules
│
└─ Still having issues?
   └─ See CLOUD_SETUP.md troubleshooting section
```

## 📈 Scaling Flow (Future)

```
Application Traffic Increases
│
├─ Monitor Cloud Run metrics
│  └─ Request rate
│  └─ Error rate
│  └─ Latency
│
├─ Monitor Cloud SQL metrics
│  └─ CPU usage
│  └─ Memory usage
│  └─ Connection count
│
├─ Scale if needed
│  ├─ Cloud Run: Increase memory/CPU
│  ├─ Cloud SQL: Increase tier
│  └─ Frontend: Enable Cloud CDN
│
└─ Retest and monitor
```

---

**Use this guide to visualize:**
- ✅ How components connect
- ✅ Deployment process flow
- ✅ Request routing after deployment
- ✅ Security measures in place
- ✅ Time estimates
- ✅ Decision making for deployment method

**Next: Choose your deployment method and begin!** 🚀
