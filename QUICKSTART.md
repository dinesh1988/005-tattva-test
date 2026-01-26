# Quick Start Guide

## 1. Get Firebase Service Account Key (2 minutes)

1. Go to https://console.firebase.google.com/
2. Select or create a project
3. Click gear icon ⚙️ → **Project Settings**
4. Go to **Service accounts** tab
5. Click **Generate new private key**
6. Save as `firestore-service-account.json` in the `VedAstroPy` folder

## 2. Set Environment Variables

**Option A: Using .env file (Recommended)**
```bash
# Copy the example
cp VedAstroPy\.env.example VedAstroPy\.env

# Edit VedAstroPy\.env with your values
FIRESTORE_PROJECT_ID=your-project-id
```

**Option B: PowerShell (for testing)**
```powershell
$env:USE_FIRESTORE="true"
$env:FIRESTORE_PROJECT_ID="your-project-id"
$env:GOOGLE_APPLICATION_CREDENTIALS="VedAstroPy\firestore-service-account.json"
```

## 3. Enable Firestore in Firebase Console

1. Go to **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Start in production mode**
4. Select your region

## 4. Run the API

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start API server
python VedAstroPy\run_api.py
```

Visit: http://127.0.0.1:8000/docs

## 5. Test It

```powershell
# Generate a psychic profile
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/psychic-profile/generate?save=true" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"John Doe","birth_date":"1988-06-07","birth_time":"20:40","birth_place":"Chennai","user_id":"test_user_123"}' | ConvertTo-Json
```

Check Firestore Console to see your data!

## Troubleshooting

### "Failed to connect to Firestore"
- Check that `firestore-service-account.json` exists
- Verify `FIRESTORE_PROJECT_ID` matches your Firebase project
- Make sure Firestore is enabled in Firebase Console

### "Module not found: firebase_admin"
```powershell
pip install firebase-admin
```

### Want to use in-memory storage instead?
```powershell
$env:USE_FIRESTORE="false"
python VedAstroPy\run_api.py
```
