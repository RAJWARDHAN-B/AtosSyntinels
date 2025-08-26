#!/bin/bash

# Glean Render Deployment Script
# This script helps prepare your application for Render deployment

echo "🚀 Glean Render Deployment Preparation"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git remote add origin <your-github-repo-url>"
    exit 1
fi

# Check if all files are committed
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Please commit them first:"
    echo "   git add ."
    echo "   git commit -m 'Prepare for deployment'"
    exit 1
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote origin found. Please add your GitHub repository:"
    echo "   git remote add origin <your-github-repo-url>"
    exit 1
fi

echo "✅ Repository check passed"

# Update backend URL in frontend files for production
echo "🔧 Updating backend URLs for production..."

# Create backup of original files
cp glean/frontend/src/pages/Home.jsx glean/frontend/src/pages/Home.jsx.backup
cp glean/frontend/src/components/Chatbot.jsx glean/frontend/src/components/Chatbot.jsx.backup

# Update Home.jsx
sed -i 's|const BACKEND_URL = "http://localhost:8000";|const BACKEND_URL = process.env.VITE_BACKEND_URL || "https://glean-backend.onrender.com";|g' glean/frontend/src/pages/Home.jsx

# Update Chatbot.jsx
sed -i 's|const baseUrl = "http://localhost:8000";|const baseUrl = process.env.VITE_BACKEND_URL || "https://glean-backend.onrender.com";|g' glean/frontend/src/components/Chatbot.jsx

echo "✅ Backend URLs updated for production"

# Check if .env files exist
echo "🔍 Checking environment files..."

if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env not found. Please create it with your API keys:"
    echo "   GROQ_API_KEY=your_groq_api_key_here"
    echo "   GOOGLE_API_KEY=your_google_api_key_here"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore file..."
    cat > .gitignore << EOF
# Environment variables
.env
backend/.env
glean/frontend/.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
glean/frontend/dist/
glean/frontend/build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo "✅ .gitignore created"
fi

# Commit changes
echo "📝 Committing deployment changes..."
git add .
git commit -m "Prepare for Render deployment"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Deployment preparation complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Connect your GitHub repository"
echo "4. Render will automatically deploy both services"
echo ""
echo "Or deploy manually:"
echo "1. Create Web Service for backend"
echo "2. Create Static Site for frontend"
echo "3. Set environment variables"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "🌐 Your app will be available at:"
echo "   Frontend: https://glean-frontend.onrender.com"
echo "   Backend: https://glean-backend.onrender.com"
echo "   API Docs: https://glean-backend.onrender.com/docs"
