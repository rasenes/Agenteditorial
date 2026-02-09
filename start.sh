#!/bin/bash
# Startup script

set -e

echo "Editorial Agent IA - Startup Script"
echo "=================================="

echo "Python version:"
python --version

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

if [ ! -f ".installed" ]; then
  echo "Installing requirements..."
  pip install -r requirements.txt
  touch .installed
fi

mkdir -p backend/data backend/logs

echo "Starting Backend..."
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

wait $BACKEND_PID $FRONTEND_PID
