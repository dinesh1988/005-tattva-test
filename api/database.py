"""
Database Module for VedAstroPy API
===================================
Google Firestore integration for storing Psychic Profiles.

Supports both:
1. Google Firestore (Production)
2. In-memory storage (Development/Testing)
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

# =============================================================================
# Configuration
# =============================================================================

# Set to True to use Firestore, False for in-memory storage
USE_FIRESTORE = os.getenv("USE_FIRESTORE", "false").lower() == "true"

# Firestore settings (from environment variables)
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", "")
FIRESTORE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")  # Path to service account JSON
FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "psychic_profiles")


# =============================================================================
# In-Memory Storage (Development)
# =============================================================================

# Simple in-memory store for development
_memory_store: Dict[str, Dict[str, Any]] = {}


async def _save_to_memory(profile: dict, user_id: str) -> str:
    """Save profile to in-memory storage."""
    profile_id = str(uuid.uuid4())
    profile['id'] = profile_id
    profile['user_id'] = user_id
    profile['created_at'] = datetime.utcnow().isoformat()
    profile['_partition_key'] = user_id
    _memory_store[profile_id] = profile
    return profile_id


async def _get_from_memory(profile_id: str) -> Optional[dict]:
    """Get profile from in-memory storage."""
    return _memory_store.get(profile_id)


async def _get_user_profiles_memory(user_id: str, limit: int = 10) -> List[dict]:
    """Get all profiles for a user from in-memory storage."""
    profiles = [p for p in _memory_store.values() if p.get('user_id') == user_id]
    return profiles[:limit]


# =============================================================================
# Google Firestore Storage (Production)
# =============================================================================

_firestore_db = None


def _init_firestore():
    """Initialize Firestore client (lazy loading)."""
    global _firestore_db
    
    if _firestore_db is not None:
        return
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            if FIRESTORE_CREDENTIALS and os.path.exists(FIRESTORE_CREDENTIALS):
                cred = credentials.Certificate(FIRESTORE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (works in Cloud Run with service account)
                firebase_admin.initialize_app()
        
        _firestore_db = firestore.client()
        print(f"Connected to Firestore: {FIRESTORE_PROJECT_ID}/{FIRESTORE_COLLECTION}")
        
    except ImportError:
        raise RuntimeError(
            "Firebase Admin SDK not installed. "
            "Install with: pip install firebase-admin"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Firestore: {e}")


async def _save_to_firestore(profile: dict, user_id: str) -> str:
    """Save profile to Google Firestore."""
    _init_firestore()
    
    profile_id = str(uuid.uuid4())
    
    # Prepare document
    document = {
        'id': profile_id,
        'user_id': user_id,
        'created_at': datetime.utcnow().isoformat(),
        'type': 'psychic_profile',
        **profile
    }
    
    # Save to Firestore
    doc_ref = _firestore_db.collection(FIRESTORE_COLLECTION).document(profile_id)
    doc_ref.set(document)
    
    return profile_id


async def _get_from_firestore(profile_id: str) -> Optional[dict]:
    """Get profile from Google Firestore."""
    _init_firestore()
    
    doc_ref = _firestore_db.collection(FIRESTORE_COLLECTION).document(profile_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return None


async def _get_user_profiles_firestore(user_id: str, limit: int = 10) -> List[dict]:
    """Get all profiles for a user from Google Firestore."""
    _init_firestore()
    
    # Query profiles by user_id, ordered by created_at descending
    profiles_ref = _firestore_db.collection(FIRESTORE_COLLECTION)
    query = profiles_ref.where('user_id', '==', user_id) \
                        .where('type', '==', 'psychic_profile') \
                        .order_by('created_at', direction=firestore.Query.DESCENDING) \
                        .limit(limit)
    
    docs = query.stream()
    profiles = [doc.to_dict() for doc in docs]
    
    return profiles


# =============================================================================
# Public Interface (Auto-selects storage backend)
# =============================================================================

async def get_db():
    """Dependency for database access."""
    if USE_FIRESTORE:
        _init_firestore()
    return {"backend": "firestore" if USE_FIRESTORE else "memory"}


async def save_profile(profile: dict, user_id: str) -> str:
    """
    Save a psychic profile to the database.
    
    Args:
        profile: Profile data dictionary
        user_id: User ID for indexing
        
    Returns:
        Generated profile ID
    """
    if USE_FIRESTORE:
        return await _save_to_firestore(profile, user_id)
    else:
        return await _save_to_memory(profile, user_id)


async def get_profile_by_id(profile_id: str) -> Optional[dict]:
    """
    Retrieve a profile by its ID.
    
    Args:
        profile_id: The profile's unique ID
        
    Returns:
        Profile data or None if not found
    """
    if USE_FIRESTORE:
        return await _get_from_firestore(profile_id)
    else:
        return await _get_from_memory(profile_id)


async def get_profiles_by_user(user_id: str, limit: int = 10) -> List[dict]:
    """
    Get all profiles for a specific user.
    
    Args:
        user_id: The user's ID
        limit: Maximum number of profiles to return
        
    Returns:
        List of profile data dictionaries
    """
    if USE_FIRESTORE:
        return await _get_user_profiles_firestore(user_id, limit)
    else:
        return await _get_user_profiles_memory(user_id, limit)


async def delete_profile(profile_id: str, user_id: str = None) -> bool:
    """
    Delete a profile.
    
    Args:
        profile_id: The profile's unique ID
        user_id: The user's ID (optional, for validation)
        
    Returns:
        True if deleted, False if not found
    """
    if USE_FIRESTORE:
        _init_firestore()
        try:
            doc_ref = _firestore_db.collection(FIRESTORE_COLLECTION).document(profile_id)
            doc_ref.delete()
            return True
        except Exception:
            return False
    else:
        if profile_id in _memory_store:
            del _memory_store[profile_id]
            return True
        return False


# =============================================================================
# Firestore Best Practices Applied:
# 
# 1. Document ID: Auto-generated UUID for unique identification
# 2. Indexes: Composite index on user_id + created_at for efficient querying
# 3. Embedding: All profile data in single document (1MB limit per doc)
# 4. Lazy Connection: Only connect when needed
# 5. Service Account: Use GOOGLE_APPLICATION_CREDENTIALS for auth
# 6. Collections: Single collection with type field for filtering
# =============================================================================


# =============================================================================
# Daily Prediction Storage (Cache Layer)
# =============================================================================

def save_daily_prediction(prediction: dict, user_id: str, date: str) -> str:
    """
    Save a daily prediction to Firestore with date-based caching.
    Uses composite key: user_id + date for uniqueness.
    
    Args:
        prediction: Prediction data dictionary
        user_id: User ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        Document ID (composite: user_id_date)
    """
    if USE_FIRESTORE:
        _init_firestore()
        
        doc_id = f"{user_id}_{date}"
        
        document = {
            'id': doc_id,
            'user_id': user_id,
            'date': date,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'daily_prediction',
            **prediction
        }
        
        doc_ref = _firestore_db.collection(FIRESTORE_COLLECTION).document(doc_id)
        doc_ref.set(document)
        
        return doc_id
    else:
        # In-memory storage
        doc_id = f"{user_id}_{date}"
        _memory_store[doc_id] = {
            'id': doc_id,
            'user_id': user_id,
            'date': date,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'daily_prediction',
            **prediction
        }
        return doc_id


def get_daily_prediction(user_id: str, date: str) -> Optional[dict]:
    """
    Retrieve a cached daily prediction for a user and date.
    
    Args:
        user_id: User ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        Prediction data if exists, None otherwise
    """
    doc_id = f"{user_id}_{date}"
    
    if USE_FIRESTORE:
        _init_firestore()
        
        doc_ref = _firestore_db.collection(FIRESTORE_COLLECTION).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    else:
        # In-memory storage
        return _memory_store.get(doc_id)
