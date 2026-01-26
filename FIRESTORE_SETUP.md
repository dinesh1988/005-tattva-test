# Google Firestore Setup Guide

## 1. Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select existing project
3. Follow the setup wizard

## 2. Enable Firestore Database

1. In Firebase Console, go to **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Production mode** (with security rules)
4. Select a location (choose closest to your users)

## 3. Create Service Account

1. Go to **Project Settings** (gear icon) → **Service accounts**
2. Click **Generate new private key**
3. Save the JSON file securely (e.g., `firestore-service-account.json`)
4. **Never commit this file to Git!** Add it to `.gitignore`

## 4. Set Up Firestore Indexes

Create a composite index for efficient queries:

1. Go to **Firestore Database** → **Indexes** tab
2. Click **Add index**
3. Configure:
   - Collection ID: `psychic_profiles`
   - Fields:
     - `user_id` (Ascending)
     - `created_at` (Descending)
   - Query scope: Collection

Or use the Firebase CLI:
```bash
firebase deploy --only firestore:indexes
```

## 5. Environment Variables (Development)

Create a `.env` file in your project root:

```bash
# Enable Firestore
USE_FIRESTORE=true

# Project ID (find in Firebase Console)
FIRESTORE_PROJECT_ID=your-project-id

# Path to service account JSON
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\firestore-service-account.json

# Collection name (default: psychic_profiles)
FIRESTORE_COLLECTION=psychic_profiles
```

## 6. Environment Variables (Google Cloud Run)

When deploying to Cloud Run, you don't need the service account JSON if you:

1. Use the same project for Cloud Run and Firestore
2. Assign proper IAM roles to the Cloud Run service account

Set environment variables in Cloud Run:
```bash
gcloud run deploy vedastro-api \
  --set-env-vars="USE_FIRESTORE=true" \
  --set-env-vars="FIRESTORE_PROJECT_ID=your-project-id" \
  --set-env-vars="FIRESTORE_COLLECTION=psychic_profiles"
```

Or in the Cloud Run console:
- Go to your service → **Edit & Deploy New Revision**
- Add environment variables in the **Variables & Secrets** tab

## 7. Install Dependencies

```bash
pip install -r VedAstroPy/api/requirements.txt
```

## 8. Test Connection

Run the API with Firestore enabled:

```bash
# Windows PowerShell
$env:USE_FIRESTORE="true"
$env:FIRESTORE_PROJECT_ID="your-project-id"
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
python VedAstroPy\run_api.py
```

Check the logs for:
```
Connected to Firestore: your-project-id/psychic_profiles
```

## 9. Firestore Security Rules

In Firebase Console → Firestore Database → Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Psychic Profiles Collection
    match /psychic_profiles/{profileId} {
      // Allow read if authenticated (adjust based on your auth)
      allow read: if request.auth != null;
      
      // Allow write if user owns the profile
      allow create: if request.auth != null 
                    && request.resource.data.user_id == request.auth.uid;
      
      allow update, delete: if request.auth != null 
                            && resource.data.user_id == request.auth.uid;
    }
  }
}
```

For development/testing (open access):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true; // WARNING: Only for development!
    }
  }
}
```

## 10. Cost Management

Firestore free tier includes:
- 50,000 document reads/day
- 20,000 document writes/day
- 20,000 document deletes/day
- 1 GB storage

Monitor usage in Firebase Console → Usage and billing

## Differences from Cosmos DB

| Feature | Cosmos DB | Firestore |
|---------|-----------|-----------|
| Provider | Microsoft Azure | Google Cloud |
| Query Language | SQL-like | NoSQL (native) |
| Partition Key | Required | Not required |
| Async SDK | Yes | Sync only |
| Free Tier | 1000 RU/s (limited) | 50k reads/day |
| Best For | Azure ecosystem | GCP ecosystem |

## Troubleshooting

### "Failed to connect to Firestore"
- Check service account JSON path
- Verify FIRESTORE_PROJECT_ID matches your project
- Ensure Firestore is enabled in Firebase Console

### "Permission denied"
- Check Firestore security rules
- Verify service account has Firestore User role
- For Cloud Run, check service account IAM permissions

### "Index required"
- Firestore will provide a link to create the index
- Click the link and wait 1-2 minutes for index to build
- Or manually create composite index as described above
