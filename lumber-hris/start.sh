#!/bin/bash
# Lumber HRIS — Start Script
# Runs the FastAPI backend serving both API and frontend
cd "$(dirname "$0")"
export DATABASE_URL="sqlite:///./lumber_hris.db"
export PYTHONPATH="$(pwd)"

echo "🪵 Lumber HRIS Starting..."
echo "   Backend: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:8000"
echo ""

exec /home/node/.openclaw/workspace/.venv/bin/uvicorn backend.main:app \
  --host 0.0.0.0 --port 8000 --reload
