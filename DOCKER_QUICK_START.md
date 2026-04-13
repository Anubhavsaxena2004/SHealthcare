# 🚀 QUICK START: DEPLOYING SHEALTHCARE

## Overview

Your SHealthcare application is now ready for Docker deployment on Render! This document provides a quick start for the most common scenarios.

---

## 📋 What Was Created

✅ **Dockerfile** - Multi-stage optimized Docker image  
✅ **docker-compose.yml** - Local development with PostgreSQL  
✅ **.dockerignore** - Optimized build context  
✅ **requirements.txt** - Updated with gunicorn and requests  
✅ **.env** - Local development configuration  
✅ **.env.production** - Production template  
✅ **render.yaml** - One-click infrastructure (optional)  
✅ **RENDER_DEPLOYMENT.md** - Comprehensive guide

---

## 🔥 Quick Deploy to Render (5 minutes)

### Option 1: Manual Setup (Recommended for beginners)

1. **Create PostgreSQL Database**:
   - Go to https://render.com
   - Click "New +" → "PostgreSQL"
   - Name: `shealthcare-db`
   - Copy the connection string

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Select your GitHub repo
   - Runtime: Docker
   - Set these environment variables:
     ```
     DATABASE_URL = <from PostgreSQL>
     FLASK_ENV = production
     DEBUG = False
     GOOGLE_API_KEY = <your key>
     FLASK_SECRET_KEY = <run: python -c "import secrets; print(secrets.token_hex(32))">
     ```

3. **Deploy**:
   - Click "Create Web Service"
   - Wait ~2-3 minutes for build
   - Your app will be live at `https://your-app.onrender.com`

### Option 2: Using Blueprint (One-click)

1. Go to [Render Blueprints](https://render.com/blueprints)
2. Upload or link this repository
3. Select `render.yaml`
4. Click "Deploy"
5. Fill in required secrets
6. Done! ✨

### Option 3: Command Line (Advanced)

```bash
# Using Render CLI
render deploy --service-name shealthcare-app --branch main
```

---

## 🧪 Test Locally First

### Without Docker (requires Python installed)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python run.py

# 4. Open browser
# http://localhost:5000
```

### With Docker (Recommended)

```bash
# 1. Build and start
docker-compose up -d

# 2. Check logs
docker-compose logs -f app

# 3. Open browser
# http://localhost:5000

# 4. Stop
docker-compose down
```

---

## ✅ Deployment Checklist

Before deploying to Render:

- [ ] Google API Key obtained and saved
- [ ] Generated strong FLASK_SECRET_KEY
- [ ] Updated `requirements.txt` with any new dependencies
- [ ] Tested locally with `docker-compose up`
- [ ] GitHub repo is up to date
- [ ] No sensitive data in .env files committed to Git
- [ ] Dockerfile builds successfully: `docker build -t shealthcare .`

---

## 🔑 Important: Environment Variables

### For Production (set in Render dashboard):

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `DEBUG` | `False` |
| `DATABASE_URL` | From PostgreSQL service |
| `GOOGLE_API_KEY` | Get from https://makersuite.google.com |
| `FLASK_SECRET_KEY` | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |

### How to set in Render:

1. Go to Web Service → **Environment**
2. Add each variable
3. Click "Save"
4. Service redeploys automatically

---

## 🐛 Troubleshooting Quick Fixes

### "Build failed"
→ Check if `requirements.txt` is in root directory  
→ All dependencies are compatible with Python 3.11

### "App won't start"
→ Check **Logs** tab in Render  
→ Verify all env vars are set  
→ Test locally first: `docker-compose up`

### "Database connection error"
→ Verify `DATABASE_URL` is correct  
→ Wait 30 seconds for database to start  
→ Check PostgreSQL is running on Render dashboard

### "ModuleNotFoundError"
→ Run `pip freeze > requirements.txt` locally  
→ Commit and push to GitHub  
→ Redeploy on Render

---

## 📊 Monitoring After Deployment

1. **Logs**: `Web Service → Logs` tab
2. **Metrics**: `Web Service → Metrics` tab (CPU, RAM, Disk)
3. **Health**: Render shows service status automatically
4. **Database**: PostgreSQL service shows stats too

---

## 🔄 Making Updates

After deployment, to update your app:

```bash
# 1. Make changes locally
# 2. Test with docker
docker-compose up
# 3. Commit and push
git add .
git commit -m "Update feature"
git push origin main
# 4. Render auto-deploys! ✨
```

No manual deployment needed with auto-deploy enabled!

---

## 💡 Pro Tips

1. **Use environment variables** for all configuration
2. **Never commit `.env`** to Git (only `.env.example`)
3. **Start with "Starter Plus"** plan ($7/month) for reliability
4. **Enable auto-deploy** for seamless updates
5. **Monitor logs** when troubleshooting
6. **Use Render's shell** to run one-off commands:
   ```bash
   flask db upgrade  # Run migrations
   flask shell       # Python interactive shell
   ```

---

## 📚 Documentation Files

- **RENDER_DEPLOYMENT.md** - Comprehensive deployment guide
- **.env.example** - Environment template
- **.env.production** - Production template
- **render.yaml** - Infrastructure as code
- **Dockerfile** - Docker image definition
- **docker-compose.yml** - Local development stack

---

## 🎯 Next Steps

1. Read **RENDER_DEPLOYMENT.md** for detailed instructions
2. Test locally: `docker-compose up`
3. Deploy to Render following Option 1 or 2 above
4. Monitor logs and metrics
5. Enable auto-deploy from GitHub

---

**Questions?** Check RENDER_DEPLOYMENT.md for more details!
