@echo off
REM Rubiscape ML Pipeline Tracker - Windows Start Script

echo.
echo ============================================
echo  Rubiscape ML Pipeline Tracker
echo  Starting Services...
echo ============================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Docker not found. Using manual start mode.
    echo.
    echo Starting PostgreSQL: Ensure PostgreSQL is running on localhost:5432
    echo.
    cd backend
    echo Starting Backend...
    start "Rubiscape Backend" cmd /k "venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"
    
    cd ../frontend
    echo Starting Frontend...
    start "Rubiscape Frontend" cmd /k "npm start"
    
    cd ..
) else (
    echo Starting with Docker Compose...
    docker-compose up -d
    
    echo.
    echo ============================================
    echo  Services Started!
    echo ============================================
    echo.
    echo Frontend:  http://localhost:3000
    echo Backend:   http://localhost:8000
    echo API Docs:  http://localhost:8000/docs
    echo.
    echo View logs: docker-compose logs -f
    echo Stop all:  docker-compose down
    echo.
)

pause
