# 🚀 Glean Deployment Guide - Render

This guide will help you deploy the Glean application to Render, a cloud platform that offers a free tier and easy deployment.

## 📋 Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **API Keys**: You'll need your GROQ_API_KEY and GOOGLE_API_KEY

## 🎯 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done)
2. **Ensure all files are committed**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 2: Deploy Backend to Render

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect Your Repository**
   - Connect your GitHub account
   - Select your repository
   - Choose the branch (usually `main`)

3. **Configure Backend Service**
   - **Name**: `glean-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python main.py`
   - **Plan**: `Free`

4. **Set Environment Variables**
   - Click "Environment" tab
   - Add these variables:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     GOOGLE_API_KEY=your_google_api_key_here
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://glean-backend.onrender.com`)

### Step 3: Deploy Frontend to Render

1. **Create Another Web Service**
   - Click "New +" → "Static Site"

2. **Configure Frontend Service**
   - **Name**: `glean-frontend`
   - **Build Command**: 
     ```bash
     cd glean/frontend
     npm install
     npm run build
     ```
   - **Publish Directory**: `glean/frontend/dist`
   - **Plan**: `Free`

3. **Set Environment Variables**
   - Add this variable:
     ```
     VITE_BACKEND_URL=https://glean-backend.onrender.com
     ```
   - Replace with your actual backend URL

4. **Deploy**
   - Click "Create Static Site"
   - Wait for deployment to complete
   - Note your frontend URL (e.g., `https://glean-frontend.onrender.com`)

### Step 4: Update Frontend Configuration

1. **Update Backend URL in Frontend**
   - In your GitHub repository, update the backend URL in the frontend code
   - File: `glean/frontend/src/pages/Home.jsx`
   - Change: `const BACKEND_URL = "http://localhost:8000";`
   - To: `const BACKEND_URL = "https://glean-backend.onrender.com";`

2. **Update Chatbot Component**
   - File: `glean/frontend/src/components/Chatbot.jsx`
   - Change: `const baseUrl = "http://localhost:8000";`
   - To: `const baseUrl = "https://glean-backend.onrender.com";`

3. **Commit and Push Changes**
   ```bash
   git add .
   git commit -m "Update backend URL for production"
   git push origin main
   ```

4. **Redeploy Frontend**
   - Go to your frontend service in Render
   - Click "Manual Deploy" → "Deploy latest commit"

## 🔧 Alternative: Using render.yaml (Blue-Green Deployment)

If you want to deploy both services at once using the `render.yaml` file:

1. **Ensure render.yaml is in your repository root**
2. **Go to Render Dashboard**
3. **Click "New +" → "Blueprint"**
4. **Connect your repository**
5. **Render will automatically create both services**

## 🌐 Access Your Application

- **Frontend**: `https://glean-frontend.onrender.com`
- **Backend API**: `https://glean-backend.onrender.com`
- **API Documentation**: `https://glean-backend.onrender.com/docs`

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

2. **CORS Errors**
   - Ensure your backend CORS settings include your frontend URL
   - Check that environment variables are set correctly

3. **API Key Issues**
   - Verify GROQ_API_KEY and GOOGLE_API_KEY are set in Render
   - Check that keys are valid and have sufficient credits

4. **Service Not Starting**
   - Check the service logs in Render dashboard
   - Verify the start command is correct
   - Ensure the health check path exists

### Debug Mode

To enable debug logging, add this environment variable to your backend service:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Monitoring

1. **Service Health**: Monitor service status in Render dashboard
2. **Logs**: View real-time logs for debugging
3. **Metrics**: Track performance and usage
4. **Alerts**: Set up notifications for service issues

## 🔄 Continuous Deployment

Render automatically redeploys when you push changes to your GitHub repository. To disable this:

1. Go to your service settings
2. Toggle off "Auto-Deploy"
3. Use manual deployments instead

## 💰 Cost Management

- **Free Tier**: Includes 750 hours/month for web services
- **Static Sites**: Always free
- **Custom Domains**: Free with SSL certificates
- **Upgrades**: Available for higher usage

## 🚀 Performance Optimization

1. **Enable Caching**: Configure caching headers for static assets
2. **Compress Responses**: Enable gzip compression
3. **Optimize Images**: Use WebP format and proper sizing
4. **Minimize Dependencies**: Remove unused packages

## 🔒 Security

1. **Environment Variables**: Never commit API keys to your repository
2. **HTTPS**: Render provides free SSL certificates
3. **CORS**: Configure CORS properly for production
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## 📞 Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Community Forum**: [community.render.com](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)

---

**🎉 Congratulations! Your Glean application is now deployed and accessible worldwide!**
