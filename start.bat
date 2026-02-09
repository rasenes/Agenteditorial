@echo off
REM Startup script (Windows) - One command experience

echo.
echo Editorial Agent IA - One Command
echo ===============================
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
echo Checking providers...
python -m backend.cli doctor

echo.
echo Running AUTO pipeline (no docs, no clicks)...
echo.
python -m backend.cli run --trends 10 --count 12 --remix --out backend\data\latest_run.json

echo.
echo Optional: start API + UI dashboards
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.

start "Editorial Agent - Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 2 >nul

start "Editorial Agent - Frontend" cmd /k "streamlit run frontend\app.py"

timeout /t 2 >nul
start http://localhost:8501

echo.
echo Done. Latest run saved to backend\data\latest_run.json
pause
