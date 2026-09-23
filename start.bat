@echo off
setlocal EnableExtensions

set METPAY_PORT=8001

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

set "VENV_PY=%CD%\.venv\Scripts\python.exe"

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    )
)

echo Installing dependencies...
"%VENV_PY%" -m pip install -e ".[dev]"
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Starting MetPay...
start "MetPay" "%VENV_PY%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port %METPAY_PORT%

echo Waiting for http://127.0.0.1:%METPAY_PORT% ...
set /a _tries=0
:wait_ready
set /a _tries+=1
if %_tries% gtr 60 (
    echo Server did not become ready in time. Check the "MetPay" window for errors.
    exit /b 1
)
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%METPAY_PORT%/health' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -ne 200) { exit 1 } } catch { exit 1 }"
if errorlevel 1 goto wait_ready

echo Open http://127.0.0.1:%METPAY_PORT%/payments-ui
start "" "http://127.0.0.1:%METPAY_PORT%/payments-ui"
echo MetPay is ready. Keep the "MetPay" window open to leave the server running.
pause

endlocal
