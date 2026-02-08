@echo off
REM Démarrage rapide du projet Editorial Agent (Windows)

echo.
echo 🚀 Editorial Agent IA - Startup Script
echo ========================================
echo.

REM Vérifier Python
echo ✓ Python version:
python --version
echo.

REM Créer venv si nécessaire
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activation venv
call venv\Scripts\activate.bat

REM Installer requirements
if not exist "backend\__pycache__" (
    echo 📦 Installing requirements...
    pip install -r requirements.txt
)

REM Créer les dossiers nécessaires
if not exist "backend\data" mkdir backend\data
if not exist "backend\logs" mkdir backend\logs
if not exist "frontend" mkdir frontend

echo.
echo 🎯 Starting Editorial Agent...
echo 📊 Backend: http://localhost:8000
echo 🎨 Frontend: http://localhost:8501
echo.

REM Open terminal for Backend
echo Starting Backend...
start "Editorial Agent - Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Small delay
timeout /t 2

REM Open terminal for Frontend
echo Starting Frontend...
start "Editorial Agent - Frontend" cmd /k "streamlit run frontend\app.py"

echo.
echo ✨ Editorial Agent is starting...
echo Press any terminal to close or use Ctrl+C
pause
