# VedAstroPy Deployment Guide

Complete guide for deploying VedAstroPy API to Google Cloud Run.

## 🚀 Quick Deploy

### Prerequisites

1. **Install Google Cloud SDK:**
   ```bash
   # Windows
   choco install gcloudsdk
   
   # Mac
   brew install --cask google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

3. **Create/Select Project:**
   ```bash
   gcloud projects create vedastro-project --name="VedAstro"
   gcloud config set project vedastro-project
   ```

### One-Command Deploy

```bash
# Make script executable (Mac/Linux)
chmod +x deploy.sh

# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh production
```

**Windows PowerShell:**
```powershell
# Set variables
$env:GCLOUD_PROJECT_ID="vedastro-project"
$env:GCLOUD_REGION="us-central1"

# Deploy
gcloud run deploy vedastro-api `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2
```

---

## 📋 Manual Deployment Steps

### 1. Build Docker Image Locally (Optional Testing)

```bash
# Build
docker build -t vedastro-api .

# Test locally
docker run -p 8080:8080 vedastro-api

# Visit http://localhost:8080/docs
```

### 2. Deploy to Cloud Run

```bash
# Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Deploy
gcloud run deploy vedastro-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### 3. Set Environment Variables

```bash
gcloud run services update vedastro-api \
  --region us-central1 \
  --set-env-vars "ENVIRONMENT=production,VERSION=0.6.0"
```

### 4. Configure Custom Domain (Optional)

```bash
gcloud run domain-mappings create \
  --service vedastro-api \
  --domain api.vedastro.org \
  --region us-central1
```

---

## 🔄 CI/CD with Cloud Build

### Setup Automated Deployment

1. **Connect GitHub Repository:**
   - Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
   - Click "Connect Repository"
   - Select your GitHub repo
   - Authorize access

2. **Create Build Trigger:**
   ```bash
   gcloud builds triggers create github \
     --repo-name=VedAstro \
     --repo-owner=YOUR_GITHUB_USERNAME \
     --branch-pattern="^main$" \
     --build-config=VedAstroPy/cloudbuild.yaml
   ```

3. **Every push to `main` branch will auto-deploy!**

---

## 🔐 Security Best Practices

### 1. Use Secret Manager

```bash
# Create secret
echo -n "your-database-url" | gcloud secrets create database-url --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding database-url \
  --member=serviceAccount:YOUR-PROJECT-NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Mount secret
gcloud run services update vedastro-api \
  --region us-central1 \
  --set-secrets=DATABASE_URL=database-url:latest
```

### 2. Enable Authentication (Optional)

```bash
# Require authentication
gcloud run services update vedastro-api \
  --region us-central1 \
  --no-allow-unauthenticated
```

---

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
gcloud run logs tail vedastro-api --region us-central1

# Last 50 entries
gcloud run logs read vedastro-api --region us-central1 --limit 50
```

### View Metrics
```bash
# Open in console
gcloud run services describe vedastro-api --region us-central1
```

**Or visit:** https://console.cloud.google.com/run

---

## 💰 Cost Optimization

### Free Tier Limits
- **2M requests/month free**
- **360,000 GB-seconds free**
- **180,000 vCPU-seconds free**

### Reduce Costs
```bash
# Reduce memory for low traffic
gcloud run services update vedastro-api \
  --region us-central1 \
  --memory 1Gi \
  --min-instances 0 \
  --max-instances 5
```

---

## 🧪 Testing Deployment

### Test Endpoints

```bash
# Health check
curl https://YOUR-SERVICE-URL/health

# API documentation
open https://YOUR-SERVICE-URL/docs

# Test yoga calculation
curl -X POST https://YOUR-SERVICE-URL/api/yogas/check \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1994-06-13T23:40:00",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata"
  }'
```

---

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
gcloud run logs read vedastro-api --region us-central1 --limit 100

# Common issues:
# 1. Port not set to $PORT (should be 8080)
# 2. Missing dependencies in requirements.txt
# 3. Swiss Ephemeris files not downloaded
```

### Out of Memory
```bash
# Increase memory
gcloud run services update vedastro-api \
  --region us-central1 \
  --memory 4Gi
```

### Slow Performance
```bash
# Increase CPU
gcloud run services update vedastro-api \
  --region us-central1 \
  --cpu 4

# Or use min-instances to avoid cold starts
gcloud run services update vedastro-api \
  --region us-central1 \
  --min-instances 1
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 🎯 Deployment Checklist

- [ ] Install Google Cloud SDK
- [ ] Authenticate with `gcloud auth login`
- [ ] Create/select GCP project
- [ ] Enable required APIs
- [ ] Configure environment variables
- [ ] Run `./deploy.sh` or manual deploy
- [ ] Test all endpoints
- [ ] Set up monitoring/alerts
- [ ] Configure custom domain (optional)
- [ ] Set up CI/CD (optional)
- [ ] Review security settings
- [ ] Monitor costs

**Your VedAstroPy v0.6.0 API is now ready for deployment! 🚀**
