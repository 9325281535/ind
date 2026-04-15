#!/bin/bash

# Rubiscape ML Pipeline Tracker - Unix Start Script

echo ""
echo "============================================"
echo "  Rubiscape ML Pipeline Tracker"
echo "  Starting Services..."
echo "============================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "WARNING: Docker not found. Using manual start mode."
    echo ""
    echo "Starting PostgreSQL: Ensure PostgreSQL is running on localhost:5432"
    echo ""
    
    # Start Backend
    echo "Starting Backend..."
    (
        cd backend
        source venv/bin/activate
        uvicorn app.main:app --reload --port 8000
    ) &
    
    # Start Frontend
    echo "Starting Frontend..."
    (
        cd frontend
        npm start
    ) &
    
    echo ""
    echo "Processes started in background."
    echo "Press Ctrl+C to stop."
else
    echo "Starting with Docker Compose..."
    docker-compose up -d
    
    echo ""
    echo "============================================"
    echo "  Services Started!"
    echo "============================================"
    echo ""
    echo "Frontend:  http://localhost:3000"
    echo "Backend:   http://localhost:8000"
    echo "API Docs:  http://localhost:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop all:  docker-compose down"
    echo ""
fi
