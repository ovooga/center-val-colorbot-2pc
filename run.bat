@echo off

:: Auto-elevate to Administrator (UAC prompt)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo ========================================
echo    Centre colorBot Launcher
echo ========================================
echo.

:: Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Start Centre colorBot using venv Python
echo [*] Starting Centre colorBot...
echo.

:: Use venv Python directly
venv\Scripts\python.exe main.py

:: Pause if error occurred
if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with error
    pause
)

