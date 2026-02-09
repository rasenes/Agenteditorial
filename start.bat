@echo off
REM Startup script (Windows)

echo.
echo Editorial Agent IA - Startup Script
echo ==================================
echo.

echo Python version:
python --version
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist ".installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    type nul > .installed
)

if not exist "backend\data" mkdir backend\data
if not exist "backend\logs" mkdir backend\logs

echo.
echo Starting Editorial Agent...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.

echo Starting Backend...
start "Editorial Agent - Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 2 >nul

echo Starting Frontend...
start "Editorial Agent - Frontend" cmd /k "streamlit run frontend\app.py"

echo.
echo Editorial Agent is starting...
echo Use Ctrl+C in each terminal to stop.
pause
