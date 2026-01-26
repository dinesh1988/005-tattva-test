# VedAstroPy - Complete Google Cloud Run Deployment 🚀

## ✅ Files Created

Your project now has complete deployment configuration:

```
VedAstroPy/
├── Dockerfile              # Optimized Python 3.11 image with Swiss Ephemeris
├── .dockerignore          # Excludes unnecessary files from build
├── deploy.sh              # One-command deployment script
├── cloudbuild.yaml        # Automated CI/CD configuration
├── .env.example           # Environment variable template
└── DEPLOYMENT.md          # Complete deployment guide
```

---

## 🎯 Quick Start

### Option 1: One-Command Deploy (Recommended)

```bash
# Install Google Cloud SDK first (if needed)
# Windows: choco install gcloudsdk
# Mac: brew install --cask google-cloud-sdk

# Authenticate
gcloud auth login

# Deploy!
chmod +x deploy.sh
./deploy.sh production
```

### Option 2: Windows PowerShell

```powershell
# Set project
$env:GCLOUD_PROJECT_ID = "vedastro-project"

# Deploy
gcloud run deploy vedastro-api `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2
```

---

## 📦 What's Deployed

- **FastAPI Application** (main.py) with 20+ endpoints
- **21 Yoga Functions** (4 Moon, 5 Mahapurusha, 7 Wealth, 5 Raja)
- **Swiss Ephemeris** (automatic download in container)
- **Auto-scaling** (0 to 10 instances)
- **Health checks** (new `/health` endpoint)

---

## 🔍 Test After Deployment

```bash
# Get service URL
gcloud run services describe vedastro-api --region us-central1 --format 'value(status.url)'

# Test health
curl https://YOUR-URL/health

# Test yoga calculation
curl -X POST https://YOUR-URL/api/yogas/check \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1994-06-13T23:40:00",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata"
  }'
```

---

## 💰 Cost Estimate

**Free Tier (Monthly):**
- 2M requests free
- 360,000 GB-seconds free
- 180,000 vCPU-seconds free

**Your Config (2GB RAM, 2 CPU):**
- ~$0.00008 per request after free tier
- ~50,000 requests = $4/month
- ~500,000 requests = $40/month

---

## 🔄 Auto-Deploy from GitHub

```bash
# Setup CI/CD trigger
gcloud builds triggers create github \
  --repo-name=VedAstro \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=VedAstroPy/cloudbuild.yaml
```

Every push to `main` branch will auto-deploy!

---

## 📊 Monitor

```bash
# View logs
gcloud run logs tail vedastro-api --region us-central1

# Open console
echo "https://console.cloud.google.com/run"
```

---

## 🎉 What's New in v0.6.0

- ✅ **21 Yogas Operational** (22% complete)
- ✅ **Vasumathi Discovery** (75% frequency in famous people!)
- ✅ **Production-Ready API** (FastAPI + Swiss Ephemeris)
- ✅ **Full Cloud Deployment** (Google Cloud Run optimized)

**Next Steps:** Deploy and share your API with the world! 🌍

---

For complete guide, see [DEPLOYMENT.md](DEPLOYMENT.md)
