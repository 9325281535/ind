# Quick Start Guide - Rubiscape ML Pipeline Tracker

## 🚀 Fastest Way to Get Running (5 minutes)

### Prerequisites Check
- [ ] Have Docker installed? ([Install Docker](https://www.docker.com/products/docker-desktop))
- [ ] Have PostgreSQL 12+ installed? OR willing to use Docker
- [ ] Have Python 3.9+ installed? ([Install Python](https://www.python.org/downloads/))
- [ ] Have Node.js 18+ installed? ([Install Node.js](https://nodejs.org/))

---

## Option A: Docker Compose (Easiest - 2 commands)

```bash
# 1. Start everything in Docker
docker-compose up -d

# 2. Open browser
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/docs
```

Done! ✅

---

## Option B: Manual Setup (Local Development)

### Step 1: Start PostgreSQL

**Windows/Mac/Linux with Docker:**
```bash
docker run --name rubiscape-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rubiscape_ml \
  -p 5432:5432 \
  -d postgres:15
```

**OR if you have PostgreSQL installed locally:**
- Ensure PostgreSQL is running
- Create database: `CREATE DATABASE rubiscape_ml;`
- Update backend `.env` with connection string

### Step 2: Start Backend

```bash
cd execution-project/backend

# Create & activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at: http://localhost:8000
📚 API Docs at: http://localhost:8000/docs

### Step 3: Start Frontend (New Terminal)

```bash
cd execution-project/frontend

npm install
npm start
```

✅ Frontend running at: http://localhost:3000

---

## Test Everything Works

### Quick Health Check
```bash
# In terminal:
curl http://localhost:8000/health

# Should return:
# {"status":"ok","service":"Rubiscape ML Pipeline Tracker"}
```

### Create Your First Pipeline
```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Pipeline",
    "description": "Test pipeline",
    "pipeline_type": "training",
    "created_by": "admin"
  }'
```

### View in Dashboard
1. Open http://localhost:3000
2. See your pipeline in the dashboard
3. Click "Start" to change state
4. Watch it update in real-time! 🎉

---

## Common Commands

### Using Docker Compose
```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View all running services
docker-compose ps
```

### Backend Development
```bash
# Run tests
pytest

# Check API documentation
# http://localhost:8000/docs

# Stop server
Ctrl+C

# Restart with changes auto-reload
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

---

## Troubleshooting

### "Connection refused" on Backend
- PostgreSQL not running
- **Fix**: Ensure Docker PostgreSQL is running: `docker ps | grep postgres`

### "API not responding" in Frontend
- Backend not running on port 8000
- **Fix**: Check terminal where backend is running, check port: `lsof -i :8000`

### "Port already in use"
```bash
# Find process using port 8000 (change 8000 to your port)
lsof -i :8000

# Kill it
kill -9 <PID>

# Or change port in uvicorn command
uvicorn app.main:app --reload --port 8080
```

### "Module not found - scipy, numpy, etc"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Fresh start everything
```bash
# Remove all Docker containers and volumes
docker-compose down -v

# Remove node_modules
rm -rf frontend/node_modules

# Reinstall everything
docker-compose up -d
cd frontend && npm install
```

---

## Next Steps

1. ✅ **Create pipelines** - Use the dashboard to create test pipelines
2. 📊 **Explore API** - Visit http://localhost:8000/docs for interactive API docs
3. 🔧 **Customize** - Update pipeline types and states in `backend/app/models.py`
4. 📚 **Learn More** - See [README.md](./README.md) and [SETUP.md](./SETUP.md)

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Full Setup Guide**: See [SETUP.md](./SETUP.md)
- **Project Details**: See [README.md](./README.md)

---

**You're all set! 🎉 Happy pipeline tracking!**
