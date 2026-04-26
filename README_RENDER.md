# 🚀 Render Deployment Guide for Research Topic Discovery Platform

## ✅ Files Created for Render

Your project now includes all necessary files for Render deployment:

### Docker Files:
- `Dockerfile` - Combined multi-stage build (frontend + backend)
- `Dockerfile.backend` - Backend-only deployment
- `Dockerfile.frontend` - Frontend-only deployment
- `docker-compose.yml` - Local testing with Docker Compose
- `nginx.conf` - Nginx configuration for serving frontend + proxying API

### Render Configuration:
- `render.yaml` - Infrastructure as Code blueprint for Render
- `build-backend.sh` - Build script for Render backend service
- `DEPLOY_RENDER.md` - Comprehensive deployment instructions

### Frontend Configuration:
- `frontend/.env.example` - Environment variable template

---

## 🎯 Quick Deploy Steps

### Method 1: Using render.yaml (Recommended - One Click!)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment files"
   git push origin main
   ```

2. **Deploy to Render**
   - Go to https://render.com/dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the `render.yaml` file
   - Click "Apply"

3. **Wait for deployment** (~5-10 minutes)
   - Render will automatically create:
     - PostgreSQL database (free tier)
     - Backend web service (free tier)
     - Frontend static site (free tier)

4. **Access your app**
   - Frontend: `https://research-frontend.onrender.com`
   - Backend API: `https://research-backend.onrender.com/api/v1`

---

### Method 2: Manual Deployment

#### Step 1: Create PostgreSQL Database
1. Go to https://render.com/dashboard
2. Click "New +" → "PostgreSQL"
3. Choose "Free" plan
4. Note the **Internal Database URL**

#### Step 2: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name:** `research-backend`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Add environment variables:
   ```
   DATABASE_URL=<paste-your-database-url>
   SECRET_KEY=<generate-random-32-char-string>
   AI_MODE=local
   CORS_ORIGINS=["https://your-app.onrender.com"]
   PORT=8000
   ```
5. Click "Create Web Service"

#### Step 3: Deploy Frontend
1. Click "New +" → "Static Site"
2. Connect your GitHub repo
3. Configure:
   - **Name:** `research-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
   - **Plan:** Free
4. Add environment variable:
   ```
   VITE_API_URL=https://research-backend.onrender.com/api/v1
   ```
5. Click "Create Static Site"

---

## 🔧 Environment Variables Reference

### Backend Required Variables:
```bash
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
SECRET_KEY=minimum-32-character-random-string
AI_MODE=local
CORS_ORIGINS=["https://your-domain.onrender.com"]
PORT=8000
```

### Backend Optional Variables:
```bash
# For enhanced AI features (not required - works free without these!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# For higher academic API rate limits
SEMANTIC_SCHOLAR_API_KEY=your-key
```

### Frontend Optional Variables:
```bash
# Only needed if deploying frontend separately from backend
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

---

## 🐛 Troubleshooting Common Issues

### Issue: "Database connection error"
**Fix:**
- Ensure PostgreSQL database is created and healthy
- Use the **Internal Database URL** from Render dashboard
- Check database credentials in environment variables

### Issue: "CORS error" in browser console
**Fix:**
- Update `CORS_ORIGINS` in backend to include your frontend URL
- Format: `["https://research-frontend.onrender.com"]`
- Redeploy backend after changing CORS settings

### Issue: "404 Not Found" on frontend
**Fix:**
- Ensure build command runs successfully
- Check that `dist/` folder exists after build
- Verify publish directory is set to `dist`

### Issue: "API requests failing"
**Fix:**
- Set `VITE_API_URL` environment variable in frontend
- Format: `https://research-backend.onrender.com/api/v1`
- Ensure backend service is running (check Render logs)

### Issue: "Build timeout"
**Fix:**
- Free tier has 15-minute build timeout
- Optimize build by using cached dependencies
- Consider upgrading to paid plan if builds consistently timeout

---

## 💰 Cost Estimate (FREE Tier)

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| PostgreSQL | Free | $0 (90-day expiry, then manual renewal) |
| Backend Web Service | Free | $0 (750 hours/month) |
| Frontend Static Site | Free | $0 (unlimited bandwidth) |
| **Total** | | **$0/month** |

**Note:** Render's free tier databases expire after 90 days of inactivity. To keep it active:
- Make at least one query every 90 days
- Or upgrade to paid plan ($7/month)

---

## 📊 Monitoring Your Deployment

1. **View Logs:**
   - Go to service dashboard on Render
   - Click "Logs" tab to see real-time logs

2. **Check Health:**
   - Backend health endpoint: `https://your-backend.onrender.com/health`
   - Should return: `{"status":"healthy"}`

3. **Monitor Performance:**
   - Render dashboard shows CPU, memory, and request metrics
   - Set up alerts for downtime notifications

---

## 🔄 Updating Your Deployment

After making code changes:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render automatically deploys on every push to the connected branch!

---

## 🎉 Success Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created
- [ ] Backend service deployed and healthy
- [ ] Frontend service deployed and accessible
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health check passing
- [ ] No errors in logs

---

## 📞 Need Help?

1. Check Render logs in dashboard
2. Review `DEPLOY_RENDER.md` for detailed instructions
3. Test locally with Docker Compose first:
   ```bash
   docker-compose up --build
   ```
4. Visit Render community forum: https://community.render.com

**Your platform is 100% FREE to run - no API keys required!** 🎊
