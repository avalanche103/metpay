@echo off
setlocal

cd /d "%~dp0"

if not exist "backend" (
    echo Backend folder was not found.
    exit /b 1
)

cd backend

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Check that Python is installed.
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    )
)

echo Installing dependencies...
python -m pip install -e ".[dev]"
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Starting MetPay...
echo Open http://127.0.0.1:8000/payments-ui
start "" "http://127.0.0.1:8000/payments-ui"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

endlocal
