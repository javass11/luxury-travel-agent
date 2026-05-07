@echo off
REM Luxury Travel Agent - Windows Setup Script
REM This script sets up the entire development environment on Windows

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  LUXURY TRAVEL AGENT - Windows Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >/dev/null 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Python found. Checking pip...
pip --version >/dev/null 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please reinstall Python and ensure pip is included
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [3/5] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Setting up environment variables...
(
    echo SECRET_KEY=dev-secret-key-for-local-testing
    echo DEBUG=true
    echo CORS_ORIGINS=http://localhost:3000,http://localhost:5000,http://localhost:5173
) > .env

echo [5/5] Initializing database...
python -c "from src.app import app; from src.models import db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"

if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SETUP COMPLETE!
echo ============================================================
echo.
echo Your development environment is ready!
echo.
echo To start the app, run:
echo   python -m src.app
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo.
echo To stop the app, press Ctrl+C
echo.
pause
