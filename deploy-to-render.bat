@echo off
chcp 65001 >nul

echo 🚀 Glean Render Deployment Preparation
echo ======================================

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not found. Please initialize git first:
    echo    git init
    echo    git add .
    echo    git commit -m "Initial commit"
    echo    git remote add origin ^<your-github-repo-url^>
    pause
    exit /b 1
)

REM Check if all files are committed
git diff --quiet
if errorlevel 1 (
    echo ⚠️  You have uncommitted changes. Please commit them first:
    echo    git add .
    echo    git commit -m "Prepare for deployment"
    pause
    exit /b 1
)

REM Check if remote is set
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo ❌ No remote origin found. Please add your GitHub repository:
    echo    git remote add origin ^<your-github-repo-url^>
    pause
    exit /b 1
)

echo ✅ Repository check passed

REM Update backend URL in frontend files for production
echo 🔧 Updating backend URLs for production...

REM Create backup of original files
copy "glean\frontend\src\pages\Home.jsx" "glean\frontend\src\pages\Home.jsx.backup"
copy "glean\frontend\src\components\Chatbot.jsx" "glean\frontend\src\components\Chatbot.jsx.backup"

REM Update Home.jsx (using PowerShell for text replacement)
powershell -Command "(Get-Content 'glean\frontend\src\pages\Home.jsx') -replace 'const BACKEND_URL = \"http://localhost:8000\";', 'const BACKEND_URL = process.env.VITE_BACKEND_URL || \"https://glean-backend.onrender.com\";' | Set-Content 'glean\frontend\src\pages\Home.jsx'"

REM Update Chatbot.jsx
powershell -Command "(Get-Content 'glean\frontend\src\components\Chatbot.jsx') -replace 'const baseUrl = \"http://localhost:8000\";', 'const baseUrl = process.env.VITE_BACKEND_URL || \"https://glean-backend.onrender.com\";' | Set-Content 'glean\frontend\src\components\Chatbot.jsx'"

echo ✅ Backend URLs updated for production

REM Check if .env files exist
echo 🔍 Checking environment files...

if not exist "backend\.env" (
    echo ⚠️  backend\.env not found. Please create it with your API keys:
    echo    GROQ_API_KEY=your_groq_api_key_here
    echo    GOOGLE_API_KEY=your_google_api_key_here
)

REM Create .gitignore if it doesn't exist
if not exist ".gitignore" (
    echo 📝 Creating .gitignore file...
    (
        echo # Environment variables
        echo .env
        echo backend/.env
        echo glean/frontend/.env
        echo.
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo build/
        echo develop-eggs/
        echo dist/
        echo downloads/
        echo eggs/
        echo .eggs/
        echo lib/
        echo lib64/
        echo parts/
        echo sdist/
        echo var/
        echo wheels/
        echo *.egg-info/
        echo .installed.cfg
        echo *.egg
        echo MANIFEST
        echo.
        echo # Virtual environments
        echo venv/
        echo env/
        echo ENV/
        echo.
        echo # Node.js
        echo node_modules/
        echo npm-debug.log*
        echo yarn-debug.log*
        echo yarn-error.log*
        echo.
        echo # Build outputs
        echo glean/frontend/dist/
        echo glean/frontend/build/
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignore
    echo ✅ .gitignore created
)

REM Commit changes
echo 📝 Committing deployment changes...
git add .
git commit -m "Prepare for Render deployment"

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git push origin main

echo.
echo 🎉 Deployment preparation complete!
echo ======================================
echo.
echo Next steps:
echo 1. Go to https://dashboard.render.com
echo 2. Click "New +" → "Blueprint"
echo 3. Connect your GitHub repository
echo 4. Render will automatically deploy both services
echo.
echo Or deploy manually:
echo 1. Create Web Service for backend
echo 2. Create Static Site for frontend
echo 3. Set environment variables
echo.
echo 📖 See DEPLOYMENT_GUIDE.md for detailed instructions
echo.
echo 🌐 Your app will be available at:
echo    Frontend: https://glean-frontend.onrender.com
echo    Backend: https://glean-backend.onrender.com
echo    API Docs: https://glean-backend.onrender.com/docs
echo.
pause
