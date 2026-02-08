#!/bin/bash
# Démarrage rapide du projet Editorial Agent

echo "🚀 Editorial Agent IA - Startup Script"
echo "========================================"

# Vérifier Python
echo "✓ Python version:"
python --version

# Installer dépendances si besoin
if [ ! -d "venv" ]; then
    echo "📦 Créating virtual environment..."
    python -m venv venv
fi

# Activation venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Installer requirements
if [ ! -d "backend/__pycache__" ] || [ ! -f ".installed" ]; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    touch .installed
fi

# Créer les dossiers nécessaires
mkdir -p backend/data
mkdir -p backend/logs
mkdir -p frontend

# Lancer backend et frontend en parallèle
echo "🎯 Starting Editorial Agent..."
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:8501"
echo ""

# Start backend
echo "Starting Backend..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Start frontend
echo "Starting Frontend..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
