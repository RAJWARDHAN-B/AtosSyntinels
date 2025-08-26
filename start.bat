@echo off
chcp 65001 >nul

echo 🚀 Starting Glean - AI-Powered Legal Document Analysis Platform
echo ================================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Start Backend
echo 🔧 Starting Backend Server...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found in backend directory
    echo    Please create a .env file with your API keys:
    echo    GROQ_API_KEY=your_groq_api_key_here
    echo    GOOGLE_API_KEY=your_google_api_key_here
)

REM Start backend server
echo 🚀 Starting FastAPI server on http://localhost:8000
start "Glean Backend" python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo 🎨 Starting Frontend Server...
cd ..\glean\frontend

REM Install dependencies
echo 📦 Installing Node.js dependencies...
npm install

REM Start frontend server
echo 🚀 Starting React development server on http://localhost:3000
start "Glean Frontend" npm run dev

echo.
echo 🎉 Glean is now running!
echo ================================================================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
echo ================================================================

pause

REM Stop all processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo 👋 Goodbye!
pause
