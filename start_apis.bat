@echo off
echo 🔥 DECLUTTERED.AI - Starting All API Servers
echo =============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python detected
echo 🚀 Starting all API servers...
echo.

REM Run the Python server manager
python start_apis.py

echo.
echo 🛑 All servers stopped
pause