# Research Topic Discovery Platform - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Option 1: Deploy with Docker Compose (Recommended)

Render supports Docker deployments. Follow these steps:

#### Step 1: Create a Web Service on Render
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure as follows:

**Basic Settings:**
- **Name:** `research-platform`
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** Leave blank

**Build & Deploy Settings:**
- **Runtime:** `Docker`
- **Dockerfile:** `Dockerfile.backend` (we'll create a combined one below)
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```
DATABASE_URL=postgresql://user:password@your-render-db-host:5432/research_platform
SECRET_KEY=generate-a-random-secret-key-here
AI_MODE=local
CORS_ORIGINS=["https://your-domain.onrender.com","http://localhost:5173"]
PORT=8000
```

#### Step 2: Create PostgreSQL Database on Render
1. Go to https://render.com/dashboard
2. Click "New +" → "PostgreSQL"
3. Choose your plan (Free tier available)
4. Copy the **Internal Database URL**
5. Use this URL in your Web Service's `DATABASE_URL` environment variable

#### Step 3: Deploy Frontend Separately
1. Create another Web Service
2. **Root Directory:** `frontend`
3. **Build Command:** `npm install && npm run build`
4. **Start Command:** `npx serve dist -l $PORT`
5. **Environment Variables:**
   ```
   VITE_API_URL=https://your-backend-service.onrender.com/api/v1
   PORT=8000
   ```

---

### Option 2: Single Combined Dockerfile for Render

Create a `Dockerfile` in the root that serves both frontend and backend:

```dockerfile
# Multi-stage build for full-stack deployment
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy built frontend to nginx
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 80

# Start both services
CMD service nginx start && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;

        # Serve static frontend files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://localhost:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

---

## 🔧 Environment Variables for Render

### Required Variables:
```bash
# Database (get from Render PostgreSQL dashboard)
DATABASE_URL=postgresql://user:password@hostname:5432/dbname

# Security
SECRET_KEY=your-generated-secret-key-min-32-chars
ALGORITHM=HS256

# AI Configuration (FREE - no keys needed!)
AI_MODE=local

# CORS (update with your actual Render URLs)
CORS_ORIGINS=["https://your-app.onrender.com"]

# Port (Render sets this automatically)
PORT=8000
```

### Optional Variables:
```bash
# If you want enhanced AI features later
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# For higher rate limits on academic APIs
SEMANTIC_SCHOLAR_API_KEY=your-key
```

---

## 📝 render.yaml (Blueprint for Render)

Create a `render.yaml` file in your root directory for Infrastructure as Code:

```yaml
services:
  # Backend API Service
  - type: web
    name: research-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "./build-backend.sh"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: research-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: AI_MODE
        value: local
      - key: CORS_ORIGINS
        value: '["https://research-platform.onrender.com"]'
      - key: PORT
        value: 8000

  # Frontend Static Site
  - type: web
    name: research-frontend
    env: static
    region: oregon
    plan: free
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: ./frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://research-backend.onrender.com/api/v1

databases:
  - name: research-db
    databaseName: research_platform
    user: research_user
    plan: free
```

---

## 🐛 Common Deployment Issues & Solutions

### Issue 1: Database Connection Error
**Solution:** 
- Ensure PostgreSQL database is created and running
- Use the **Internal Database URL** from Render dashboard
- Check that database migrations have run

### Issue 2: CORS Errors
**Solution:**
- Update `CORS_ORIGINS` to include your Render frontend URL
- Format: `["https://your-app.onrender.com"]`

### Issue 3: Build Fails - Missing Dependencies
**Solution:**
- Check `requirements.txt` has all dependencies
- Ensure `package.json` is in the correct directory
- Add build logs inspection in Render dashboard

### Issue 4: Port Binding Error
**Solution:**
- Render requires using `$PORT` environment variable
- Update start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Issue 5: Static Files Not Serving
**Solution:**
- Ensure frontend builds successfully (`npm run build`)
- Check `dist/` folder exists after build
- Verify nginx or serve configuration points to correct directory

---

## ✅ Pre-Deployment Checklist

Before deploying to Render:

- [ ] All code committed to GitHub
- [ ] `Dockerfile` or `Dockerfile.backend` created
- [ ] `requirements.txt` up to date
- [ ] `package.json` has all dependencies
- [ ] Environment variables configured
- [ ] PostgreSQL database created on Render
- [ ] CORS origins updated with Render URLs
- [ ] Secret key generated (min 32 characters)
- [ ] AI_MODE set to "local" (free mode)

---

## 🎯 One-Click Deploy Alternative

If you prefer a simpler setup, consider these alternatives:

### Railway.app
- Automatically detects Docker setup
- One-click PostgreSQL provisioning
- Easier environment variable management

### Fly.io
- Great for full-stack apps
- Built-in PostgreSQL
- Free tier available

### Vercel (Frontend) + Render (Backend)
- Deploy frontend to Vercel (optimized for React)
- Deploy backend to Render
- Connect via API URL

---

## 📞 Support

If deployment fails:
1. Check Render build logs in dashboard
2. Verify all environment variables are set
3. Test locally with Docker Compose first
4. Review error messages in Render logs

The platform is designed to work **100% free** without any paid API keys!
