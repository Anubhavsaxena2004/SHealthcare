# 🚀 RENDER DEPLOYMENT GUIDE FOR SHEALTHCARE

This guide will help you deploy the SHealthcare application to Render with Docker containerization.

## Prerequisites

Before you begin, ensure you have:
- ✅ A Render account (https://render.com)
- ✅ GitHub repository with your SHealthcare code
- ✅ Google API Key (for AI features)
- ✅ Docker and Docker Compose installed locally (optional, for testing)

---

## 📋 Table of Contents

1. [Local Testing with Docker](#local-testing)
2. [Setting up on Render](#render-setup)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Troubleshooting](#troubleshooting)

---

## 🧪 Local Testing with Docker {#local-testing}

### Prerequisites
- Docker and Docker Compose installed
- Google API Key

### Step 1: Set up environment

```bash
# Create .env file from example
cp .env.example .env

# Update .env with your credentials
# Edit .env and add:
# - GOOGLE_API_KEY=your_actual_key
# - FLASK_SECRET_KEY=your_secret_key
```

### Step 2: Build and run locally

```bash
# Build the Docker image
docker-compose build

# Start services (Flask app + PostgreSQL)
docker-compose up -d

# Check logs
docker-compose logs -f app

# Initialize database (if needed)
docker-compose exec app flask db upgrade

# Stop services
docker-compose down
```

### Step 3: Access the application

- **Application**: http://localhost:5000
- **Database**: localhost:5432

---

## ☁️ Setting up on Render {#render-setup}

### Step 1: Create a PostgreSQL Database on Render

1. Log in to https://render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `shealthcare-db`
   - **Database**: `shealthcare`
   - **User**: `shealthcare_user`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15
4. Click "Create Database"
5. **Save the connection string** - you'll need it for the web service

### Step 2: Create a Web Service on Render

1. Log in to https://render.com
2. Click "New +" → "Web Service"
3. Select **"Deploy an existing image from a registry"** OR **"Build and deploy from a Git repository"**

#### Option A: Deploy from Docker Registry (Recommended for simplicity)

1. Choose "Deploy an existing image from a registry"
2. Configure:
   - **Image URL**: `python:3.11-slim` (base image, we'll build ours)
   - Actually, **we recommend Option B below** for better control

#### Option B: Deploy from GitHub (Best for Auto-Updates)

1. Choose "Build and deploy from a Git repository"
2. Configure:
   - **Repository**: Select your GitHub repo
   - **Branch**: `main` or `master`
   - **Runtime**: `Docker`
   - **Build Command**: Leave empty (Render will auto-detect Dockerfile)
   - **Start Command**: 
     ```
     gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
     ```

3. **Instance Settings**:
   - **Plan**: Start with "Free" or "Starter Plus"
   - **Region**: Choose your region
   - **Auto-deploy**: Enable (auto-deploy on push to main)

4. Click "Create Web Service"

### Step 3: Connect Database to Web Service

After creating the Web Service:

1. Go to the Web Service → **Environment** tab
2. Add the following environment variables:

```env
DATABASE_URL=postgresql://shealthcare_user:<PASSWORD>@<HOST>:5432/shealthcare
FLASK_ENV=production
FLASK_SECRET_KEY=<GENERATE_RANDOM_KEY>
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
DEBUG=False
```

**Where to find these values:**
- `<PASSWORD>`: From PostgreSQL database creation
- `<HOST>`: From PostgreSQL database internal connection string
- `<GENERATE_RANDOM_KEY>`: Run locally:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

### Step 4: Initialize Database

After the web service is running:

1. In Render dashboard, find your web service
2. Go to **Shell** tab (in the top navigation)
3. Run database migrations:
   ```bash
   flask db upgrade
   ```

---

## 🔐 Environment Variables {#environment-variables}

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `FLASK_SECRET_KEY` | Secret key for sessions | `abc123def456...` |
| `FLASK_ENV` | Environment mode | `production` |
| `GOOGLE_API_KEY` | Google AI API key | `AIzaSyD...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `WORKERS` | Number of gunicorn workers | `4` |
| `TIMEOUT` | Request timeout (seconds) | `120` |

### Generating FLASK_SECRET_KEY

Run this locally:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste in Render environment variables.

---

## 🗄️ Database Setup {#database-setup}

### First Time Setup

1. **Create PostgreSQL database** (see Step 1 above)
2. **Add DATABASE_URL** to web service environment
3. **Run migrations** in web service shell:
   ```bash
   flask db upgrade
   ```

### Viewing Database Logs

In Render PostgreSQL database dashboard:
1. Go to **Logs** to check database activity
2. Use **Connection Info** to connect with pgAdmin or DBeaver if needed

### Backing up Database

Render automatically provides backups. To download:
1. Go to PostgreSQL database → **Backups**
2. Download any available backup

---

## 🐛 Troubleshooting {#troubleshooting}

### Service won't start

1. **Check logs**: Go to **Logs** tab in Render dashboard
2. **Common errors**:
   - `ModuleNotFoundError`: Check requirements.txt is up to date
   - `DATABASE_URL not found`: Verify environment variable is set
   - `Connection refused`: Database might not be ready, wait ~30 seconds

3. **Manual rebuild**:
   - Go to **Settings** → **Manual Deploy** → **Deploy latest commit**

### Database connection errors

```bash
# In Render shell, test connection:
psql $DATABASE_URL -c "SELECT 1"
```

If fails, verify:
- Database is running
- DATABASE_URL is correct
- Firewall allows connections

### Application runs locally but not on Render

Ensure:
1. ✅ `Dockerfile` exists in root directory
2. ✅ `requirements.txt` is updated with all dependencies
3. ✅ All environment variables are set
4. ✅ No hardcoded file paths (use relative paths)
5. ✅ Check **Logs** for specific error messages

### Memory/Performance Issues

1. Reduce worker count:
   ```
   gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
   ```

2. Increase instance size in Render settings

3. Enable caching for static files

---

## 📊 Monitoring

### View Logs

```bash
# On Render dashboard: Logs tab
# Real-time logs from your application
```

### Health Check

Render automatically checks if service is running. You can also test:
```bash
curl https://your-render-app.onrender.com/
```

### Metrics

Render provides CPU, Memory, and Disk usage in **Metrics** tab.

---

## 🔄 Deployment Workflow

### Automatic Deployment (Recommended)

1. Push to GitHub `main` branch
2. Render automatically rebuilds and deploys
3. Old version remains active until new version starts
4. Zero-downtime deployments

### Manual Deployment

1. Go to Web Service → **Settings** → **Manual Deploy**
2. Click **Deploy latest commit**

---

## 📝 Additional Notes

### File Structure Required for Render

```
/
├── Dockerfile              ← Required
├── .dockerignore           ← Required
├── requirements.txt        ← Required
├── run.py                  ← Entry point
├── app/                    ← Flask app
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── services.py
├── migrations/             ← Database migrations
├── diabetes_model.pkl      ← ML model
├── heart_model.pkl         ← ML model
└── .env.example           ← Template (don't commit real .env)
```

### Cost Estimation

- **Free Tier**: Limited, okay for testing
- **Starter Plus** ($7/month): Recommended for small production apps
- **Standard** ($12/month): For moderate traffic
- **PostgreSQL**: Typically $9-17/month depending on usage

### Security Best Practices

1. ✅ Never commit `.env` file to Git
2. ✅ Use strong `FLASK_SECRET_KEY` (done above)
3. ✅ Set `DEBUG=False` in production
4. ✅ Keep dependencies updated
5. ✅ Use HTTPS (Render provides free SSL)
6. ✅ Limit API key exposure

---

## 🆘 Support

If you encounter issues:

1. Check **Logs** in Render dashboard
2. Test locally with `docker-compose up`
3. Verify all environment variables are set
4. Check Render status page: https://status.render.com
5. Contact Render support: https://render.com/support

---

## 📚 Quick Reference Commands

```bash
# Local testing
docker-compose build
docker-compose up -d
docker-compose down
docker-compose logs -f app

# Database management (in Render shell)
flask db upgrade
flask shell

# Check Python version
python --version

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

**Happy Deploying! 🎉**

For more Render documentation: https://render.com/docs
For Flask documentation: https://flask.palletsprojects.com/
