@echo off
chcp 65001 > nul

set "PYTHON_EXE=python"

REM Check if Python is installed
where %PYTHON_EXE% >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not found. Please install Python and add it to your PATH.
    echo Download Python from: https://www.python.org/downloads/windows/
    pause
    exit /b 1
 )

REM Enter backend directory
cd backend

REM Check if virtual environment exists, create if not
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install dependencies
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies.
    pause
    exit /b 1
)

REM Start Flask server
echo Starting AI Secretary backend server...
%PYTHON_EXE% src/main.py

pause