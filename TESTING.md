# Testing & Deployment Guide

## Pre-Launch Testing

### 1. Backend API Testing

#### Health Check
```bash
curl -s http://localhost:8000/health | jq
# Expected: {"status":"ok","service":"Rubiscape ML Pipeline Tracker"}
```

#### Swagger/OpenAPI Docs
```
http://localhost:8000/docs
```
- Interactive API documentation
- Try endpoints directly in browser
- View request/response schemas

#### Create Pipeline (cURL)
```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Processing Pipeline",
    "description": "Processes customer data",
    "pipeline_type": "data_ingestion",
    "created_by": "test_user"
  }'
```

#### List Pipelines
```bash
curl http://localhost:8000/api/v1/pipelines | jq
```

#### Update Pipeline State
```bash
# Replace {pipeline_id} with the actual ID from create response
curl -X PATCH http://localhost:8000/api/v1/pipelines/{pipeline_id} \
  -H "Content-Type: application/json" \
  -d '{
    "current_state": "RUNNING",
    "transition_reason": "Started by user",
    "triggered_by": "test_user"
  }'
```

#### View Dashboard Summary
```bash
curl http://localhost:8000/api/v1/dashboard/summary | jq
```

### 2. Frontend Testing

#### Manual Testing Checklist
- [ ] Dashboard loads
- [ ] Summary cards show correct counts
- [ ] Can create new pipeline
- [ ] Can filter by state
- [ ] Can update pipeline state (Start/Complete/Fail)
- [ ] Real-time updates working (30 second refresh)
- [ ] Responsive design on mobile

#### Test Scenarios

**Scenario 1: Create and Track a Pipeline**
1. Click "New Pipeline"
2. Fill in:
   - Name: "Test Data Pipeline"
   - Type: "data_ingestion"
   - Description: "Testing pipeline tracking"
3. Click "Create Pipeline"
4. Verify pipeline appears in list
5. Click "Start" button
6. Verify state changed to "RUNNING"
7. Click "Complete"
8. Verify state changed to "COMPLETED"

**Scenario 2: Filter by State**
1. Click on "Running" filter button
2. Only running pipelines should appear
3. Click "Completed" filter
4. Only completed pipelines should appear
5. Click "All" to reset

**Scenario 3: Check Real-time Updates**
1. Open dashboard in two browser windows side by side
2. Create pipeline in one window
3. Verify it appears in other window within 5 seconds

### 3. Database Testing

#### Connect to PostgreSQL
```bash
# Using psql (if installed)
psql -U postgres -h localhost -d rubiscape_ml

# List tables
\dt

# Query pipelines
SELECT * FROM pipelines;

# Query audit logs
SELECT * FROM audit_logs;
```

#### Verify Table Structure
```sql
-- Check pipelines table
\d pipelines

-- Check state history
\d pipeline_state_history

-- Check audit logs
\d audit_logs
```

## Performance Testing

### Load Testing
```bash
# Using Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:8000/api/v1/pipelines

# Using wrk (if installed)
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/pipelines
```

### Response Time Testing
```bash
# Time a request
time curl -s http://localhost:8000/api/v1/pipelines > /dev/null

# Should complete in <100ms for first request
```

## Security Testing

### CORS Verification
```bash
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v http://localhost:8000/api/v1/pipelines
```

### SQL Injection Test (Should fail)
```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'; DROP TABLE pipelines; --",
    "pipeline_type": "training",
    "created_by": "admin"
  }'
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] No console errors in browser
- [ ] No error logs in backend
- [ ] Database backups created
- [ ] Environment variables configured
- [ ] CORS origins updated for production
- [ ] SSL certificates obtained (for HTTPS)

### Setting Environment Variables

#### For Render.com
```
DATABASE_URL=<your-postgresql-url>
SECRET_KEY=<generate-secure-key>
ENVIRONMENT=production
CORS_ORIGINS=["https://yourdomain.com"]
```

#### For Self-Hosted
Update `.env` files:
```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:password@your-host:5432/rubiscape_ml
SECRET_KEY=your-secure-secret-key
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
```

### Deployment Steps

#### Option 1: Render.com
1. Push code to GitHub
2. Log in to render.com
3. Create New → Web Service
4. Connect GitHub repo
5. Configure:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

#### Option 2: Docker Deployment
```bash
# Build images
docker build -t rubiscape-backend ./backend
docker build -t rubiscape-frontend ./frontend

# Push to registry
docker tag rubiscape-backend myregistry/rubiscape-backend:1.0
docker push myregistry/rubiscape-backend:1.0

# Run on production server
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 3: Kubernetes
```bash
# Create deployment manifests
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Scale as needed
kubectl scale deployment backend-app --replicas=3
```

## Monitoring & Logs

### View Backend Logs
```bash
# Docker
docker-compose logs -f backend

# Local
# Check terminal where uvicorn is running
```

### View Frontend Logs
```bash
# Docker
docker-compose logs -f frontend

# Local
# Check browser console (F12)
```

### Production Monitoring
- Set up log aggregation (ELK, Datadog, etc.)
- Monitor database performance
- Track API response times
- Monitor error rates
- Set up alerts

## Rollback Procedure

### If Deployment Fails
```bash
# Docker
docker-compose down
docker-compose up -d  # with previous version

# Render.com
# Use "Redeploy from Previous Deploy" button
```

### Database Rollback
```bash
# PostgreSQL restore from backup
psql -U postgres -d rubiscape_ml < backup.sql
```

## Performance Optimization

### Database Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM pipelines WHERE current_state = 'RUNNING';

-- Rebuild indexes
REINDEX TABLE pipelines;
REINDEX TABLE pipeline_state_history;
REINDEX TABLE audit_logs;
```

### Backend Optimization
- Enable gzip compression
- Implement caching headers
- Use connection pooling
- Monitor query performance
- Add pagination to list endpoints

### Frontend Optimization
- Code splitting with React.lazy()
- Image optimization
- CSS minification
- JavaScript bundling
- Service worker caching

## Maintenance

### Regular Tasks
- [ ] Weekly: Check error logs
- [ ] Weekly: Backup database
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review performance metrics
- [ ] Quarterly: Security audit

### Update Dependencies
```bash
# Backend
pip list --outdated
pip install --upgrade fastapi sqlalchemy pydantic

# Frontend
npm update
npm audit fix
```

---

**Last Updated**: April 15, 2026
**Status**: Production Ready ✅
